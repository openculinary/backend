echo "Please provide the mail account username"
read username

echo "Please provide the mail account password"
read -s password

kubectl delete secret backend-contact-mail
kubectl create secret generic backend-contact-mail \
  --from-literal=username=${username} \
  --from-literal=password=${password}
