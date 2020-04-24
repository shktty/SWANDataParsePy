#-*- coding: UTF-8 -*-
import struct
from PIL import Image, ImageDraw, ImageFont#pip install pillow
import numpy as np
from cv2 import cv2 as cv2#pip install opencv-python
import bz2
from bz2 import decompress
import os
import datetime
import time
import re
import requests
workpath="Y:/www/jjs/currentdata/pic/radar/png/"
basemap="Y:/www/jjs/currentdata/pic/radar/gzmap_sb.png"
sbfile="Y:/www/jjs/currentdata/pic/radar/sebiao.png"
cimissUser="yourUserName000"
cimissPsw="111"
def deleteOldFiles(dirs,fnameRex,delDays):
	#获得当前日期
	today = datetime.date.today()
	#获得历史日期，本例中为14天之前
	twoweek= datetime.timedelta(days=-1*delDays)  
	leastday = today + twoweek
	files = os.listdir(dirs)
	for f in files:
		destfile = os.path.join(dirs,f)
		if (os.path.isfile(destfile)):
			fsize = os.path.getsize(destfile)
			if fsize<1000:
				#print("无效文件,删除",imglocal)
				os.remove(destfile)
				return
			name = os.path.splitext(f)[0]
			postfix = os.path.splitext(f)[1]
			#print(postfix)
			#获得文件后缀，只是针对.000文件
			if (postfix.lower() == fnameRex.lower()):
				#print(name)
				#获得该文件的创建日期，modifytime为元组
				modifytime = time.localtime((os.path.getmtime(destfile)))
				year = modifytime[0]
				month = modifytime[1]
				day = modifytime[2]
				#将日期初始化为date对象
				filedate = datetime.date(year, month, day)
				#比较日期，删除较早的文件
				if (leastday > filedate):
					print("删除",destfile)
					os.remove(destfile)
def readInt(f,byteCount):
	return struct.unpack('<i', f.read(byteCount))[0]
def readShort(f,byteCount):
	return struct.unpack('<h', f.read(byteCount))[0]
def readChar(f,byteCount):
	return struct.unpack('b', f.read(byteCount))[0]
def readStr(f,byteCount):
	return str(f.read(byteCount).decode('GBK','ignore')).strip()
def readFloat(f,byteCount):
	return struct.unpack('<f', f.read(byteCount))[0]
def putText(img,text,left,top,fontsize):
	cv2img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) # cv2和PIL中颜色的hex码的储存顺序不同
	pilimg = Image.fromarray(cv2img)	 
	# PIL图片上打印汉字
	draw = ImageDraw.Draw(pilimg) # 图片上打印
	font = ImageFont.truetype("simhei.ttf", fontsize, encoding="utf-8") # 参数1：字体文件路径，参数2：字体大小
	draw.text((top, left), text, (0, 0, 0), font=font) # 参数1：打印坐标，参数2：文本，参数3：字体颜色，参数4：字体	 
	# PIL图片转cv2 图片
	cv2charimg = cv2.cvtColor(np.array(pilimg), cv2.COLOR_RGB2BGR)
	return cv2charimg
def ymdToBJT(ymdhis):
	thisdate=datetime.datetime.strptime(ymdhis,"%Y%m%d%H%M%S")
	thisdateBJT=thisdate+datetime.timedelta(hours=8)
	thisdateBJT_str=thisdateBJT.strftime("%Y%m%d%H%M%S")
	return thisdateBJT_str
def pic_superpose(path_img_logo,path_img_out,RadarStationName):
	filepath, shotname, extension=get_filePath_fileName_fileExt(path_img_logo)
	ymdhis=shotname[15:29]	
	thisdate=datetime.datetime.strptime(ymdhis,"%Y%m%d%H%M%S")
	thisdateBJT=thisdate+datetime.timedelta(hours=8)
	thisdateBJT_str=thisdateBJT.strftime("%Y{y}%m{m}%d{d}%H{H}%M{M}").format(y='年', m='月', d='日',H='时',M='分')
	
	img = cv2.imread(basemap)#背景图的读取
	co = cv2.imread(path_img_logo,-1)#需要插入图的读取
	scr_channels = cv2.split(co)
	dstt_channels = cv2.split(img)
	b, g, r, a = cv2.split(co)
	for i in range(3):
		dstt_channels[i]= dstt_channels[i]*(255.0-a)/255
		dstt_channels[i]+= np.array(scr_channels[i]*(a/255), dtype=np.uint8)
	imgout=cv2.merge(dstt_channels)
	cv2.imwrite(path_img_out,imgout)

	img1=Image.open(path_img_out)
	img2=Image.open(sbfile)
	img1.paste(img2,(10, 550))
	img1.save(path_img_out)

	imgout = cv2.imread(path_img_out)	
	imgout =putText(imgout, "贵州省"+thisdateBJT_str+"雷达回波拼图",5,5,46)
	rds="站点:"
	for rd in RadarStationName:  
		if rd!="":
			rds=rds+rd.replace(" ", "")+","
	imgout =putText(imgout, rds[:-1],1050,0,26)
	cv2.imwrite(path_img_out,imgout)


	print("生成："+path_img_out)
	# img2 = cv2.imread(filepath + shotname + "_out.png")
	# cv2.imshow("imgout", img2)
	# cv2.waitKey(0)	
def numpyToimg(datas,imgpath,XNumgrids,YNumgrids):
	dbz5=(199,195,255,0)
	dbz10=(122,112,239,0)
	dbz15=(24, 36, 215,0)
	dbz20=(165,255,173)
	dbz25=(0, 235, 0)
	dbz30=(16, 147, 24)
	dbz35=(255, 247, 98)
	dbz40=(207, 203, 0)
	dbz45=(141, 143, 0)
	dbz50=(255, 175, 173)
	dbz55=(255, 100, 82)
	dbz60=(239, 0, 48)
	dbz65=(215, 143, 255)
	dbz70=(173, 36, 255)
	img1 = Image.new("RGBA",(XNumgrids,YNumgrids))
	for i in range(datas.shape[0]):
		for j in range(datas.shape[1]):		
			data=datas[i][j]
			rgb=(0,0,0,0)
			if data>0:
				rgb=dbz5
			if data>5:
				rgb=dbz10
			if data>10:
				rgb=dbz15
			if data>15:
				rgb=dbz20
			if data>20:
				rgb=dbz25
			if data>25:
				rgb=dbz30
			if data>30:
				rgb=dbz35
			if data>35:
				rgb=dbz40
			if data>40:
				rgb=dbz45						
			if data>45:
				rgb=dbz50	
			if data>50:
				rgb=dbz55	
			if data>55:
				rgb=dbz60	
			if data>60:
				rgb=dbz60	
			if data>65:
				rgb=dbz65
			if data>70:
				rgb=dbz70
			img1.putpixel((i,j),rgb)	
	out=img1.resize((XNumgrids*2,YNumgrids*2))
	out.save(imgpath)
	#这里最后还差把两幅图片叠加起来
def get_filePath_fileName_fileExt(fileUrl):
	"""
	获取文件路径， 文件名， 后缀名
	:param fileUrl:
	:return:
	"""
	filepath, tmpfilename = os.path.split(fileUrl)
	shotname, extension = os.path.splitext(tmpfilename)
	return filepath.strip(), shotname.strip(), extension.strip()
def get_zhCN(str):#提取字符串中的中文，因为读取的字符串有乱码
	line = str.strip()  # 处理前进行相关的处理，包括转换成Unicode等
	pattern = re.compile('[^\u4e00-\u9fa5]')  # 中文的编码范围是：\u4e00到\u9fa5
	zh = " ".join(pattern.split(line)).strip()
	# zh = ",".join(zh.split())
	outStr = zh  # 经过相关处理后得到中文的文本
	return outStr
def readFiles(files):
	filepath, shotname, extension=get_filePath_fileName_fileExt(files)
	f=bz2.BZ2File(files, 'rb')
	diamond=readStr(f,12)
	dataname=readStr(f,38)
	flag=readStr(f,8)
	version=readStr(f,8)
	year=readShort(f,2)
	month=readShort(f,2)
	day=readShort(f,2)
	hour=readShort(f,2)
	minute=readShort(f,2)
	interval=readShort(f,2)
	XNumgrids=readShort(f,2)
	YNumgrids=readShort(f,2)
	ZNumgrids=readShort(f,2)
	RadarCount=readInt(f,4)
	StartLon=readFloat(f,4)
	StartLat=readFloat(f,4)
	CenterLon=readFloat(f,4)
	CenterLat=readFloat(f,4)
	XReso=round(readFloat(f,4),2)
	YReso=round(readFloat(f,4),2)
	RadarStationName=[]
	for i in range(40):
		zhGrid=readFloat(f,4)
		#print(zhGrid)
	for i in range(20):
		RadarStationName.append(get_zhCN(readStr(f,16)))
	for i in range(20):
		rdLon=readFloat(f,4)
	for i in range(20):
		rdLat=readFloat(f,4)
	for i in range(20):
		rdAlti=readFloat(f,4)
	for i in range(20):
		mosaic=f.read(1)
	Reserved=f.read(172)
	datas=np.zeros((XNumgrids,YNumgrids))
	# f1=open('D:/websites/zysqxj/yby/lightning/heatdatas.txt','w+',encoding='GBK')
	for j in range(YNumgrids):
		for i in range(XNumgrids):
			data=readChar(f,1)
			if data <0 :
				datas[i][j]=(data+256-66)/2.0
			elif data==0:
				datas[i][j]=0.0
			else:
				datas[i][j]=(data-66)/2.0
			#print(StartLon+i*XReso,",",i,",",j,",",StartLat-j*YReso,":",datas[i][j])
			# if datas[i][j]>0:
				# f1.write("{\"lng:\""+str(StartLon+i*XReso)+",\"lat:\""+str(StartLat-j*YReso)+",\"count:\""+str(datas[i][j])+"},\n")
	#f1.write(RadarStationName[2]+dataname)
	#f1.close()
	f.close()
	print(diamond,dataname,flag,RadarCount,version,RadarStationName[2],StartLon,StartLat,XNumgrids,YNumgrids,XReso,YReso)
	numpyToimg(datas,workpath+ shotname + "_emp.png",XNumgrids,YNumgrids)
	ymdhis=shotname[15:29]
	ymdhis_bjt=ymdToBJT(ymdhis)
	outpic=(workpath+shotname+".JPG").replace(ymdhis,ymdhis_bjt)
	pic_superpose(workpath+ shotname + "_emp.png",outpic.replace(".bin",""),RadarStationName)
#url_分布式数据库="http://10.203.7.71:8080/DataService?requestType=getData&directory=SWAN_PRODUCT/LOCAL/NCRAD/TDPRODUCT/MCR/&fileName=Z_OTHE_RADAMCR_20190827004200.BIN.BZ2"
def getFilesCimiss():
	timeend=(datetime.datetime.now()+datetime.timedelta(hours=-8)).strftime("%Y%m%d%H%M%S")
	timestart=(datetime.datetime.now()+datetime.timedelta(hours=-11)).strftime("%Y%m%d%H%M%S")
	url="http://10.203.89.55/cimiss-web/api?userId="+cimissUser+""\
		"&pwd="+cimissPsw+"&interfaceId=getRadaFileByTimeRange&elements=FILE_NAME_ORIG"\
		"&dataCode=RADA_SWAN_L3_MCR&timeRange=["+timestart+","+timeend+"]&"\
		"orderBy=datetime:desc&dataFormat=json"
	res=requests.get(url)
	if res.status_code == 200:		
		rjson=res.json()
		rows=rjson['DS']
		for row in rows:
			FILE_URL=row['FILE_URL']
			FILE_NAME_ORIG=row['FILE_NAME_ORIG']
			if not os.path.exists(workpath+FILE_NAME_ORIG):
				downFilesCimiss(FILE_URL,FILE_NAME_ORIG)
	else:
		print('获取文件失败')
def downFilesCimiss(FILE_URL,FILE_NAME_ORIG):
	rsp = requests.get(FILE_URL, stream=True)
	try:
		rsp.raise_for_status()
	except Exception as exc:
		print('There was a problem: %s' % (exc))
	print("下载:"+FILE_NAME_ORIG)
	playFile = open(workpath+FILE_NAME_ORIG, 'wb')
	for chunk in rsp.iter_content(512):
		if chunk:
			playFile.write(chunk)
	playFile.close()

#Main-functions
if __name__ == "__main__":
	if not os.path.exists(workpath):
		os.makedirs(workpath)
	deleteOldFiles(workpath,".bz2",2)
	deleteOldFiles(workpath,".png",2)
	deleteOldFiles(workpath,".JPG",2)
	getFilesCimiss()
	files = os.listdir(workpath)
	for f in files:
		name = os.path.splitext(f)[0]
		postfix = os.path.splitext(f)[1].lower()
		if postfix=='.bz2':
			ymdhis=name[15:29]
			ymdhis_bjt=ymdToBJT(ymdhis)
			outpic=(workpath+name+".JPG").replace(ymdhis,ymdhis_bjt)
			if not os.path.exists(outpic.replace(".bin","")):
				readFiles(workpath + f)