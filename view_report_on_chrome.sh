
echo THIS WILL CLOSE YOUR CHROME BROWSER WINDOW. PLEASE SAVE YOUR WORK BEFORE PROCEEDING
echo "ARE YOU SURE TO PROCEED? (y/n)"
read choice
if [ $choice = "y" ] || [ $choice = "Y" ]
then
  pkill Chrome;
  sleep 1
  open -a Google\ Chrome --args --disable-web-security --allow-file-access-from-files "$(pwd)/index.html";
else
  echo No window opened;
fi