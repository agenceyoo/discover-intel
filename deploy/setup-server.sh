#!/bin/bash
# ============================================================
# Script de deploiement Discover Intel sur un VPS Ubuntu/Debian
#
# Usage (une seule commande depuis votre Mac) :
#   ssh root@VOTRE_IP 'bash -s' < deploy/setup-server.sh
#
# Ou bien sur le serveur :
#   curl -sL https://raw.githubusercontent.com/agenceyoo/discover-intel/main/deploy/setup-server.sh | bash
# ============================================================
set -e

REPO="https://github.com/agenceyoo/discover-intel.git"
INSTALL_DIR="/opt/discover"

echo "========================================="
echo " Discover Intel - Installation serveur"
echo "========================================="

# 1. Mise a jour systeme et dependances
echo "[1/8] Mise a jour systeme..."
apt-get update -qq
apt-get install -y -qq python3 python3-venv python3-pip nginx certbot python3-certbot-nginx git

# 2. Creer l'utilisateur
echo "[2/8] Creation utilisateur discover..."
if ! id "discover" &>/dev/null; then
    useradd --system --create-home --shell /bin/bash discover
fi

# 3. Cloner le depot GitHub
echo "[3/8] Clonage du depot GitHub..."
if [ -d "$INSTALL_DIR/.git" ]; then
    cd $INSTALL_DIR
    sudo -u discover git pull origin main
else
    rm -rf $INSTALL_DIR
    git clone $REPO $INSTALL_DIR
    chown -R discover:discover $INSTALL_DIR
fi

# 4. Environnement virtuel Python
echo "[4/8] Creation environnement Python..."
sudo -u discover python3 -m venv $INSTALL_DIR/venv
sudo -u discover $INSTALL_DIR/venv/bin/pip install --quiet --upgrade pip
sudo -u discover $INSTALL_DIR/venv/bin/pip install --quiet -r $INSTALL_DIR/requirements.txt

# 5. Generer une cle secrete et configurer
echo "[5/8] Configuration production..."
SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
cat > $INSTALL_DIR/.env << EOF
FLASK_ENV=production
SECRET_KEY=${SECRET}
EOF
chown discover:discover $INSTALL_DIR/.env
chmod 600 $INSTALL_DIR/.env

# 6. Creer le dossier instance pour la DB
echo "[6/8] Preparation base de donnees..."
mkdir -p $INSTALL_DIR/instance
chown discover:discover $INSTALL_DIR/instance

# 7. Configurer systemd
echo "[7/8] Configuration systemd + nginx..."
# Creer le service avec la bonne cle
cat > /etc/systemd/system/discover.service << SVCEOF
[Unit]
Description=Discover Intel - Google Discover France Dashboard
After=network.target

[Service]
User=discover
Group=discover
WorkingDirectory=$INSTALL_DIR
EnvironmentFile=$INSTALL_DIR/.env
ExecStart=$INSTALL_DIR/venv/bin/gunicorn --workers 2 --bind 127.0.0.1:5001 --timeout 120 run:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SVCEOF

systemctl daemon-reload
systemctl enable discover

# Configurer nginx
SERVER_IP=$(hostname -I | awk '{print $1}')
cat > /etc/nginx/sites-available/discover << NGXEOF
server {
    listen 80;
    server_name $SERVER_IP;

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 120s;
    }

    location /static/ {
        alias $INSTALL_DIR/app/static/;
        expires 7d;
        add_header Cache-Control "public, immutable";
    }
}
NGXEOF

ln -sf /etc/nginx/sites-available/discover /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

# 8. Premiere collecte + demarrage
echo "[8/8] Premiere collecte de donnees + demarrage..."
sudo -u discover $INSTALL_DIR/venv/bin/python $INSTALL_DIR/seed.py
systemctl start discover

echo ""
echo "========================================="
echo " INSTALLATION TERMINEE !"
echo "========================================="
echo ""
echo " L'application tourne sur http://$SERVER_IP"
echo ""
echo " Commandes utiles :"
echo "   sudo systemctl status discover      # Voir le statut"
echo "   sudo systemctl restart discover     # Redemarrer"
echo "   sudo journalctl -u discover -f      # Voir les logs"
echo ""
echo " Pour mettre a jour le code :"
echo "   cd $INSTALL_DIR && sudo -u discover git pull"
echo "   sudo systemctl restart discover"
echo ""
echo " Pour ajouter un domaine + HTTPS :"
echo "   1. Pointer votre domaine (DNS A) vers $SERVER_IP"
echo "   2. Modifier server_name dans /etc/nginx/sites-available/discover"
echo "   3. sudo nginx -t && sudo systemctl reload nginx"
echo "   4. sudo certbot --nginx -d votre-domaine.com"
echo ""
