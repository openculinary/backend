echo "Please provide the mail account username"
read username

echo "Please provide the mail account password"
read -s password

kubectl delete secret api-verifications-mail
kubectl create secret generic api-verifications-mail \
  --from-literal=username=${username} \
  --from-literal=password=${password}
