#!/bin/bash
# ============================================================
# Script de deploiement Discover Intel sur un VPS Ubuntu/Debian
# Usage: scp -r Discover/ root@VOTRE_IP:/tmp/ && ssh root@VOTRE_IP 'bash /tmp/Discover/deploy/setup-server.sh'
# ============================================================
set -e

echo "========================================="
echo " Discover Intel - Installation serveur"
echo "========================================="

# 1. Mise a jour systeme et dependances
echo "[1/7] Mise a jour systeme..."
apt-get update -qq
apt-get install -y -qq python3 python3-venv python3-pip nginx certbot python3-certbot-nginx

# 2. Creer l'utilisateur
echo "[2/7] Creation utilisateur discover..."
if ! id "discover" &>/dev/null; then
    useradd --system --create-home --shell /bin/bash discover
fi

# 3. Copier le projet
echo "[3/7] Installation du projet..."
mkdir -p /opt/discover
cp -r /tmp/Discover/* /opt/discover/
cp -r /tmp/Discover/.env /opt/discover/ 2>/dev/null || true
chown -R discover:discover /opt/discover

# 4. Environnement virtuel Python
echo "[4/7] Creation environnement Python..."
sudo -u discover python3 -m venv /opt/discover/venv
sudo -u discover /opt/discover/venv/bin/pip install --quiet -r /opt/discover/requirements.txt

# 5. Generer une cle secrete et configurer
echo "[5/7] Configuration production..."
SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
cat > /opt/discover/.env << EOF
FLASK_ENV=production
SECRET_KEY=${SECRET}
EOF
chown discover:discover /opt/discover/.env

# Mettre a jour le service systemd avec la vraie cle
sed -i "s/CHANGEZ_MOI_avec_une_vraie_cle_secrete/${SECRET}/" /opt/discover/deploy/discover.service

# 6. Configurer systemd
echo "[6/7] Configuration systemd + nginx..."
cp /opt/discover/deploy/discover.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable discover
systemctl start discover

# 7. Configurer nginx
cp /opt/discover/deploy/nginx.conf /etc/nginx/sites-available/discover
ln -sf /etc/nginx/sites-available/discover /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

# 8. Collecte initiale
echo "[7/7] Premiere collecte de donnees..."
sudo -u discover /opt/discover/venv/bin/python /opt/discover/seed.py

echo ""
echo "========================================="
echo " INSTALLATION TERMINEE !"
echo "========================================="
echo ""
echo " L'application tourne sur http://$(hostname -I | awk '{print $1}')"
echo ""
echo " Commandes utiles :"
echo "   sudo systemctl status discover    # Voir le statut"
echo "   sudo systemctl restart discover   # Redemarrer"
echo "   sudo journalctl -u discover -f    # Voir les logs"
echo ""
echo " Pour ajouter un nom de domaine + HTTPS :"
echo "   1. Modifier /etc/nginx/sites-available/discover"
echo "      -> Remplacer VOTRE_DOMAINE.com par votre domaine"
echo "   2. sudo nginx -t && sudo systemctl reload nginx"
echo "   3. sudo certbot --nginx -d votre-domaine.com"
echo ""
