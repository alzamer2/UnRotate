import subprocess
import re
import sys

global coords,rwidth,rheight
iinnput = ".\\Vampire Game v01 p008.jpg"
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

intval_ = image_info_(iinnput)
inname = intval_[0]
suffix = intval_[1]
subprocess.Popen('.\\ImageMagick\\convert -quiet "'+iinnput+'" +repage "'+tmpA1+'"' ,shell=False , stdout=subprocess.PIPE)
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

# get all points of any line (given by its endpoint pairs) that passes through the red/black image as array of points
# extract all magenta points (blend of red and blue) and get the first and last magenta coordinates 
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

# get ww, hh, xoff, yoff and area for given set of top_left and bottom_right points
def getParms(input_1 , input_2 , input_3 , input_4):

    # make plist as rows of data so can sort
    plist=[input_1.split(','),input_2.split(','),input_3.split(','),input_4.split(',')]
	# sort point
    plist_x =[]
    plist_y =[]
    for i in pointlist:
        plist_x[len(plist_x):] =  [int(i[0])]
        plist_y[len(plist_y):] =  [int(i[1])]
    # sort list by x
    #xlist=`echo "$plist" | sort -g -k 1 -t ","`
    #pxArr=($xlist)
    # sort list by y
    #ylist=`echo "$plist" | sort -g -k 2 -t ","`
    #pyArr=($ylist)
    # use middle 2 coordinates for area
    tl_x = plist_x[1]
    tl_y = plist_y[1]
    br_x = plist_x[2]
    br_y = plist_y[2]
    # note: make width and height 2 px smaller and offset 1 px larger to remove all traces of background color
    # note: need abs and min, since for angles near 90, some reverse and would give negative widths
    ww = subprocess.Popen('.\\ImageMagick\\convert xc: -format "%[fx:abs((' + str(br_x) + '-' + str(tl_x) + ')-1)]" info:' ,shell=True , stdout=subprocess.PIPE).stdout.read()
    hh = subprocess.Popen('.\\ImageMagick\\convert xc: -format "%[fx:abs((' + str(br_y) + '-' + str(tl_y) + ')-1)]" info:' ,shell=True , stdout=subprocess.PIPE).stdout.read()
    
    # convert xoff,yoff to center region in image
    xoff = subprocess.Popen('.\\ImageMagick\\convert xc: -format "%[fx:ceil((' + rwidth + '-' + ww + ')/2)]" info:' ,shell=True , stdout=subprocess.PIPE).stdout.read()
    yoff = subprocess.Popen('.\\ImageMagick\\convert xc: -format "%[fx:ceil((' + rheight + '-' + hh + ')/2)]" info:' ,shell=True , stdout=subprocess.PIPE).stdout.read()
    area = int(ww)*int(hh)
    #parmsArr=($area $ww $hh $xoff $yoff)
    #print plist
    #print plist_x
    #print plist_y
    #print tl_x,tl_y,"|",br_x,br_y
    #print ww,hh,xoff,yoff,area
    #print '.\\ImageMagick\\convert xc: -format "%[fx:ceil((' + rwidth + '-' + ww + ')/2)]" info:'
    return [str(area),ww,hh,xoff,yoff]

###########################################################################################
###########################################Script##########################################
###########################################################################################


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


    #pointlist = []
    #for i in [topleftdiag,bottomrightdiag,toprightdiag,bottomleftdiag]:
    #    pointlist[len(pointlist):] = [(i,int(re.findall(',[1-9]+',i).pop().replace(',','')))]
                
        #print int(re.findall(',[1-9]+',i).pop().replace(',',''))
    #pointlist_temp=[]
    #for i in sorted(pointlist, key=lambda student: student[1]):
    #    pointlist_temp[len(pointlist_temp):] =  [i[0]]
    #pointlist = pointlist_temp
    pointlist_x=[]
    pointlist_y=[]
    pointlist = [topleftdiag.split(','),bottomrightdiag.split(','),toprightdiag.split(','),bottomleftdiag.split(',')]
    for i in pointlist:
        pointlist_x[len(pointlist_x):] =  [int(i[0])]
        pointlist_y[len(pointlist_y):] =  [int(i[1])]
    #print pointlist
    #print sorted(pointlist_x,reverse=True)
    #print sorted(pointlist_y,reverse=True)

	# put diagonal intersections in array sorted by y
	
    # get top intersections
    val_temp_ = getIntersection("0," + str(sorted(pointlist_y,reverse=True)[0]), str(widthm1) + "," + str(sorted(pointlist_y,reverse=True)[0]))
    top_left = val_temp_[1]
    top_right = val_temp_[2]
    #print top_left,top_right

    # get topcenter intersections
    val_temp_ = getIntersection("0," + str(sorted(pointlist_y,reverse=True)[1]), str(widthm1) + "," + str(sorted(pointlist_y,reverse=True)[1]))
    topcenter_left = val_temp_[1]
    topcenter_right = val_temp_[2]

    # get bottomcenter intersections
    val_temp_ = getIntersection("0," + str(sorted(pointlist_y,reverse=True)[2]), str(widthm1) + "," + str(sorted(pointlist_y,reverse=True)[2]))
    bottomcenter_left = val_temp_[1]
    bottomcenter_right = val_temp_[2]

    # get bottom intesections
    val_temp_ = getIntersection("0," + str(sorted(pointlist_y,reverse=True)[3]), str(widthm1) + "," + str(sorted(pointlist_y,reverse=True)[3]))
    bottom_left = val_temp_[1]
    bottom_right = val_temp_[2]
    #print top_left,top_right,topcenter_left,topcenter_right,bottomcenter_left,bottomcenter_right,bottom_left,bottom_right
    
    # put diagonal intersections in array sorted by x
	
    # get left intersections
    val_temp_ = getIntersection(str(sorted(pointlist_x,reverse=True)[0]) + ",0", str(sorted(pointlist_x,reverse=True)[0]) + "," + str(heightm1))
    left_top = val_temp_[1]
    left_bottom = val_temp_[2]

    # get leftcenter intersections
    val_temp_ = getIntersection(str(sorted(pointlist_x,reverse=True)[1]) + ",0", str(sorted(pointlist_x,reverse=True)[1]) + "," + str(heightm1))
    leftcenter_top = val_temp_[1]
    leftcenter_bottom = val_temp_[2]

    # get rightcenter intersections
    val_temp_ = getIntersection(str(sorted(pointlist_x,reverse=True)[2]) + ",0", str(sorted(pointlist_x,reverse=True)[2]) + "," + str(heightm1))
    rightcenter_top = val_temp_[1]
    rightcenter_bottom = val_temp_[2]

    # get right intesections
    val_temp_ = getIntersection(str(sorted(pointlist_x,reverse=True)[3]) + ",0", str(sorted(pointlist_x,reverse=True)[3]) + "," + str(heightm1))
    right_top = val_temp_[1]
    right_bottom = val_temp_[2]
    #print left_top,left_bottom,leftcenter_top,leftcenter_bottom,rightcenter_top,rightcenter_bottom,right_top,right_bottom

    # parms for top-bottom
    list_top_bottom = getParms(top_left,top_right,bottom_left,bottom_right)

    # parms for topcenter-bottomcenter
    list_topcenter_bottomcenter = getParms(topcenter_left,topcenter_right,bottomcenter_left,bottomcenter_right)

    # parms for top-bottomcenter
    list_top_bottomcenter = getParms(top_left,top_right,bottomcenter_left,bottomcenter_right)

    # parms for topcenter-bottom
    list_topcenter_bottom = getParms(topcenter_left,topcenter_right,bottom_left,bottom_right)

    # parms for left-right
    list_left_right = getParms(left_top,left_bottom,right_top,right_bottom)

    # parms for leftcenter-rightcenter
    list_leftcenter_rightcenter = getParms(leftcenter_top,leftcenter_bottom,rightcenter_top,rightcenter_bottom)

    # parms for left-rightcenter
    list_left_rightcenter = getParms(left_top,left_bottom,rightcenter_top,rightcenter_bottom)

    # parms for leftcenter-right
    list_leftcenter_right = getParms(leftcenter_top,leftcenter_bottom,right_top,right_bottom)

    # note need commas to make this work
    stack_list=[list_top_bottom,list_topcenter_bottomcenter,list_top_bottomcenter,list_topcenter_bottom,list_left_right,list_leftcenter_rightcenter,list_left_rightcenter,list_leftcenter_right]

    print stack_list
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