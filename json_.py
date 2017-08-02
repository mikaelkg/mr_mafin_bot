import json
import sys
filename="user_settingss.txt"
file=open(filename,'w',encoding="UTF-8")

filename2="user_settings.txt"
file2=open(filename2,'r',encoding="UTF-8")
text=file2.read()

json.dump([text],file)
file2.close()
file.close()

filename="user_settingss.txt"
file=open(filename,'r',encoding="UTF-8")
non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
print(str(json.load(file)).translate(non_bmp_map))
file.close()
#Привет
