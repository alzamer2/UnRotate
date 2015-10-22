import subprocess
import re
import sys

global coords
iinnput = ".\\zelda3_rot20_border10.png"
tmpA1 = ".\\temp_A_$$.mpc"
tmpA2 = ".\\temp_A_$$.cache"
tmpB1 = ".\\temp_B_$$.mpc"
tmpB2 = ".\\temp_B_$$.cache"
oouttput = ".\\zelda3_rot20_border10_out.png"

mode="inner"			# trim region 
fuzzval=0				# fuzz threshold
coords="NorthWest"		# coordinates to get color
pad=1					# border pad size
lt=0					# left edge shift of trim (+/- is right/left)
rt=0					# right edge shift of trim (+/- is right/left)
tp=0					# top edge shift of trim (+/- is down/up)
bm=0					# top bottom shift of trim (+/- is down/up)
preview="off"			# preview image


###########################################################################################
#########################################Functions#########################################
###########################################################################################
im_version =  re.findall('LIB_VERSION_NUMBER [1-9],[1-9],[1-9],[1-9]', subprocess.Popen('.\\ImageMagick\\convert -list configure' ,shell=True , stdout=subprocess.PIPE).stdout.read()).pop().replace("LIB_VERSION_NUMBER ","").split(',')
im_version = int(im_version[0])*10000000+int(im_version[1])*100000+int(im_version[2])*1000+int(im_version[3])

def image_info_(input_1):
    return subprocess.Popen('.\\ImageMagick\\convert -ping "' + input_1 + '" -format "%t,%e,%h,%w,%[fx:h-1],%[fx:w-1],%[fx:h/2],%[fx:w/2]" info:' ,shell=True , stdout=subprocess.PIPE).stdout.read().split(',')
def getIntersection(input_1 , input_2):
    #print '.\\ImageMagick\\convert ' + tmpB1 + ' ( -clone 0 -fill black -colorize 100 -fill blue +antialias -draw "line ' + input_1 + ' ' + input_2 + '" -alpha off -compose over -compose blend -composite -channel rgba -fill none +opaque magenta sparse-color:'
    Arr = subprocess.Popen('.\\ImageMagick\\convert ' + tmpB1 + ' ( -clone 0 -fill black -colorize 100 -fill blue +antialias -draw "line ' + input_1 + ' ' + input_2 + '" -alpha off ) -compose over -compose blend -composite -channel rgba -fill none +opaque magenta sparse-color:' ,shell=True , stdout=subprocess.PIPE).stdout.read().replace(",magenta","").split()
    #print Arr[len(Arr)-1]
    if len(Arr) >= 3:
        return Arr, Arr[0], Arr[len(Arr)-1]
    else:
        print "INTERSECTION ERROR"
        sys.exit()
#	(`convert $tmpB1 \
#		\( -clone 0 -fill black -colorize 100 -fill blue  \
#		+antialias -draw "line $p1 $p2" -alpha off \) \
#		-compose over -compose blend -composite \
#		-channel rgba -fill none +opaque magenta sparse-color: |\
#		sed 's/,magenta//g'`)
#	num=${#Arr[*]}
#	#echo "$num; ${Arr[*]}"
#	numm1=$((num-1))
#	if [ $num -ge 2 ]; then
#		point1=${Arr[0]}
#		point2=${Arr[$numm1]}
#	else
#		echo "INTERSECTION ERROR"
###########################################################################################
###########################################Script##########################################
###########################################################################################
intval_ = image_info_(iinnput)
inname = intval_[0]
suffix = intval_[1]
subprocess.Popen('.\\ImageMagick\\convert -quiet "'+iinnput+'" +repage "'+tmpA1+'"' ,shell=True , stdout=subprocess.PIPE)
#print im_version
# dimensions of input (rotated) image
val_temp_ = image_info_(tmpA1)
rwidth = val_temp_[3]
rheight = val_temp_[2]
rarea = int(rwidth)*int(rheight)
widthm1 = val_temp_[5]
heightm1 =  val_temp_[4]
midwidth = val_temp_[7]
midheight = val_temp_[6]

if coords.lower() == "northwest":
    coords = "0,0"
elif coords.lower() == "north":
    coords = midwidth + ",0"
elif coords.lower() == "northeast":
    coords = widthm1 + ",0"
elif coords.lower() == "east":
    coords = widthm1 + "," + midheight
elif coords.lower() == "southeast":
    coords = widthm1 + "," + heightm1
elif coords.lower() == "south":
    coords = midwidth + "," + heightm1
elif coords.lower() == "southwest":
    coords = "0," + heightm1
elif coords.lower() == "west":
    coords = "0," + midheight
elif coords.lower() == "west":
    coords = "0," + midheight
elif coords == "[1-9]+,[1-9]+":
    pass
else:
    print "--- INVALID COORDS ---"
if im_version <= 7000000:
    matte_alpha="alpha"
else:
    matte_alpha="matte"
color =  subprocess.Popen('.\\ImageMagick\\convert ' + tmpA1 + ' -format "%[pixel:u.p{' + coords + '}]" info:' ,shell=True , stdout=subprocess.PIPE).stdout.read()
if mode.lower() == "outer":
    #print '.\\ImageMagick\\convert ' + tmpA1 + ' -bordercolor ' + color + ' -border 1x1 -fuzz ' + str(fuzzval) + '% -fill none -draw "' + matte_alpha + ' ' + coords + ' floodfill" -shave 1x1 -alpha extract -format "%@" info:'
    trimbox =  subprocess.Popen('.\\ImageMagick\\convert ' + tmpA1 + ' -bordercolor ' + color + ' -border 1x1 -fuzz ' + str(fuzzval) + '% -fill none -draw "' + matte_alpha + ' ' + coords + ' floodfill" -shave 1x1 -alpha extract -format "%@" info:' ,shell=True , stdout=subprocess.PIPE).stdout.read().replace("x","+").split('+')
    ww = int(trimbox[0])
    hh = int(trimbox[1])
    xoff = int(trimbox[2])
    yoff = int(trimbox[3])
    area = ww * hh
elif mode.lower() == "inner":
    subprocess.Popen('.\\ImageMagick\\convert ' + tmpA1 + ' -bordercolor ' + color + ' -border 1x1 -fuzz ' + str(fuzzval) + '% -fill none -draw "' + matte_alpha + ' ' + coords + ' floodfill" -shave 1x1 -alpha extract -fill red -opaque white '+ tmpB1,shell=True , stdout=subprocess.PIPE)
    trpx = widthm1 + ",0"
    blpx = "0," + heightm1
    brpx = midwidth + "," + heightm1
    #print trpx,blpx,brpx
    
    val_temp_ = getIntersection("0,0",brpx)
    tlbrArr = val_temp_[0]
    topleftdiag = val_temp_[1]
    bottomrightdiag = val_temp_[2]

    val_temp_ = getIntersection(trpx,blpx)
    trblArr = val_temp_[0]
    toprightdiag = val_temp_[1]
    bottomleftdiag = val_temp_[2]
#    if [ "$topleftdiag" = "0,0" -o "$toprightdiag" = "$widthm1,0" -o "$bottomleftdiag" = "$widthm1,$heightm1" -o "$bottomleftdiag" = "0,$heightm1" ]; then
#        subprocess.Popen('.\\ImageMagick\\convert ' + tmpA1 + ' -fill none -stroke red -draw "rectangle ' + topleftdiag + ' ' + bottomrightdiag + '" show:',shell=True , stdout=subprocess.PIPE)
#        subprocess.Popen('.\\ImageMagick\\convert ' + tmpA1 + ' result_r${ang}_' + mode + '_a' + str(rarea) + '_w' + str(rwidth) + '_h' + str(rheight) + '.jpg',shell=True , stdout=subprocess.PIPE)
#    sys.exit()
#    fi
    #pointlist = [topleftdiag,bottomrightdiag,toprightdiag,bottomleftdiag]

	# get horizontal line intersections with binary image from diagonal intersection points

	# put diagonal intersections in array sorted by y
    pointlist = []
    for i in [topleftdiag,bottomrightdiag,toprightdiag,bottomleftdiag]:
        pointlist[len(pointlist):] = [(i,int(re.findall(',[1-9]+',i).pop().replace(',','')))]
                
        #print int(re.findall(',[1-9]+',i).pop().replace(',',''))
    pointlist_temp=[]
    for i in sorted(pointlist, key=lambda student: student[1]):
        pointlist_temp[len(pointlist_temp):] =  [i[0]]
    pointlist = pointlist_temp
    
    # get top intersections
    val_temp_ = getIntersection("0," + pointlist[0], widthm1 + "," pointlist[0])
    top_left = val_temp_[1]
    top_right = val_temp_[2]
    print top_left,top_right

	# get topcenter intersections
	topcenter_y=`echo "${pointArr[1]}" | cut -d, -f 2`
	getIntersection "0,$topcenter_y" "$widthm1,$topcenter_y"
	topcenter_left="$point1"
	topcenter_right="$point2"

	# get bottomcenter intersections
	bottomcenter_y=`echo "${pointArr[2]}" | cut -d, -f 2`
	getIntersection "0,$bottomcenter_y" "$widthm1,$bottomcenter_y"
	bottomcenter_left="$point1"
	bottomcenter_right="$point2"

	# get bottom intesections
	bottom_y=`echo "${pointArr[3]}" | cut -d, -f 2`
	getIntersection "0,$bottom_y" "$widthm1,$bottom_y"
	bottom_left="$point1"
	bottom_right="$point2"
	#echo "bottom_left=$bottom_left; bottom_right=$bottom_right;"

#print sorted(pointlist, key=lambda student: student[1])
#print tlbrArr,topleftdiag,bottomrightdiag
#print trblArr,toprightdiag,bottomleftdiag
'''
xoff = xoff + lt
yoff = yoff + tp
ww = ww - lt + rt
hh = hh - tp + bm

brx = xoff + ww - 1
bry = yoff + hh - 1
#subprocess.Popen('.\\ImageMagick\\convert ' + tmpA1 + ' -fill none -stroke red -draw "rectangle ' + str(xoff) + ',' + str(yoff) + ' ' + str(brx) + ',' + str(bry) + '" show:',shell=True , stdout=subprocess.PIPE)
subprocess.Popen('.\\ImageMagick\\convert ' + tmpA1 + ' -fill none -stroke red -draw "rectangle ' + str(xoff) + ',' + str(yoff) + ' ' + str(brx) + ',' + str(bry) + '" "' + inname + '_preview.' + suffix + '"',shell=True , stdout=subprocess.PIPE)
subprocess.Popen('.\\ImageMagick\\convert ' + tmpA1 + '[' + str(ww) + 'x' + str(hh) + '+' + str(xoff) + '+' + str(yoff) + '] "' + oouttput + '"',shell=True , stdout=subprocess.PIPE)
print  'crop box: ' + str(ww) + 'x' + str(hh) + '+' + str(xoff) + '+' + str(yoff)
#print trpx,blpx,brpx
#width = int(info_iinnput[3])
#height = int(info_iinnput[2])
#widthm1 = int(width) - 1
#heightm1 = int(height) - 1
#print image_info_(iinnput)
#print widthm1
#raw_input()
'''