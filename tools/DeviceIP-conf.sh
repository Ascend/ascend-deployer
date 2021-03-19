#!/bin/bash

machineType=$1
standardCardNum=$2
IpPerStdCard=$3
workMode=$4
OsIp=$5
DeviceIp=$6
resultFile='./ipAssign'
declare -a OsIpArray
declare -a DeviceIpArray

if [ $# -ne 6 ] ; then
    echo "Number of params is incorrect!!"
    echo "e.g.: $0 1 0 0 SMP /tmp/OS-IP /tmp/Device-IP"
    exit 1;
fi

# 转换参数对应的deviceIp的数量
if [ $machineType -eq 1 -a $standardCardNum -eq 0 -a $IpPerStdCard -eq 0 ]; then
    ConfNum=8
elif [ $machineType -eq 2 -a $standardCardNum -eq 0 -a $IpPerStdCard -eq 0 ]; then
    ConfNum=4
elif [ $machineType -eq 3 ];then
    ConfNum=$(($standardCardNum*$IpPerStdCard))
else
    echo 'Incorrect params!!'
    exit 1
fi
if [ $ConfNum -eq 0 ]; then
    echo 'Incorrect parameter configuration!'
    exit 1
fi

# 读取文件中的IP
if [ -s $OsIp -a -s $DeviceIp ]; then
    # 1st 读取OSIP
	idx=0
	## 第一种含有~传参的形式
	if [ `head -1 $OsIp|grep '~'` ]; then
		while read line
		do
			if [ -z "$line" ]; then
			    continue
			fi
			for ip in $( echo $line|awk -F'~' '{print $1,$2}')
			do
				OsIpArray[$idx]=$ip
				let "idx+=1"
			done
			Prefix=$(echo ${OsIpArray[0]}|awk -F "." '{if ($1<256 && $1>=0 && $2<256 && $2 >=0 && $3<256 && $3>=0  && $4<256 && $4>=0){printf("%d.%d.%d",$1,$2,$3)} else {printf("-1")}}')
			if [ $Prefix == "-1" ]; then
				echo 'Os Ip is illegal'
				exit 1
			fi
			Start=$(echo ${OsIpArray[0]}|awk -F "." '{print $4}')
			Stop=$(echo ${OsIpArray[1]}|awk -F "." '{print $4}')
			idx=0
			for num in $(seq $Start $Stop)
			do
				OsIpArray[$idx]="$Prefix.$num"
				let "idx+=1"
			done
		done < $OsIp
	## 第二种列表传参的形式，可以把删选条件换为grep -v
	elif [ `wc -l $OsIp|awk '{print $1}'` -ge 1 ]; then
		while read line
		do
		    if [ -z "$line" ]; then
			    continue
			fi
			VALID_CHECK=$(echo $line|awk -F. '{if ($1<256 && $1>=0 && $2<256 && $2 >=0 && $3<256 && $3>=0  && $4<256 && $4>=0){print "yes"} else {print "no"}}')
			if [ $VALID_CHECK == "yes" ]; then
				OsIpArray[$idx]="${line}"
				let "idx+=1"
			else
				echo 'Os Ip is illegal'
				exit 1
			fi
		done < $OsIp
	else
		echo 'The format of Os ip list is improper!!!'
		exit 1
	fi
	
	# 2nd 读取DeviceIP
	idx=0
	#初始化每个网段下的数量
	ipPerSegment=0
	ipNumInOneSegment=0
	#初始化网段数
	segmentNum=0
	## 第一种含有~传参的形式
	if [ `head -1 $DeviceIp|grep '~'` ]; then
	    declare -a TempArray
		tempIdx=0
	    while read line
		do
		    if [ -z "$line" ]; then
			    continue
			fi
		    netmaskGateway=$( echo $line|awk -F'/' '{printf("%s/%s",$2,$3)}' )
			AllIp=$( echo $line|awk -F'/' '{print $1}' )
		    for ip in $( echo $AllIp|awk -F'~' '{print $1,$2}')
		    do
			    TempArray[$tempIdx]=$ip
			    let "tempIdx+=1"
		    done
		    Prefix=$(echo ${TempArray[0]}|awk -F "." '{if ($1<256 && $1>=0 && $2<256 && $2 >=0 && $3<256 && $3>=0  && $4<256 && $4>=0){printf("%d.%d.%d",$1,$2,$3)} else {printf("-1")}}')
			if [ $Prefix == "-1" ]; then
			    echo 'Device Ip is illegal'
				exit 1
			fi
		    Start=$(echo ${TempArray[0]}|awk -F "." '{print $4}')
		    Stop=$(echo ${TempArray[1]}|awk -F "." '{print $4}')
			let "tempIdx-=2"
		    for suffix in $(seq $Start $Stop)
		    do
			    DeviceIpArray[$idx]="$Prefix.$suffix/$netmaskGateway"
			    let "idx+=1"
				let "ipPerSegment+=1"
		    done
            if [ $ipPerSegment -lt $ConfNum ]; then
			    echo 'The number of IPs in the same network segment of each line must be equal!'
				echo 'It is recommended that each line configure at least the number of IPs required by each os to reduce the need for more network segments'
				exit 1
			fi
			ipNumInOneSegment=$ipPerSegment
			let "segmentNum+=1"
			ipPerSegment=0
		done < $DeviceIp

	## 第二种列表传参的形式
	elif [ `head -1 $DeviceIp|grep -v '~'` ]; then
	    let "segmentNum+=1"
		while read line
		do
		    if [ -z "$line" ]; then
			    continue
			fi
		    netmaskGateway=$( echo $line|awk -F'/' '{printf("%s/%s",$2,$3)}' )
			Ip=$( echo $line|awk -F'/' '{print $1}' )
			VALID_CHECK=$(echo $Ip|awk -F. '{if ($1<256 && $1>=0 && $2<256 && $2 >=0 && $3<256 && $3>=0  && $4<256 && $4>=0){print "yes"} else {print "no"}}')
			if [ $VALID_CHECK == "yes" ]; then
			    if [ $idx -gt 0 ]; then
			        Previous=${DeviceIpArray[$idx-1]}
				    PreviousNetmaskGateway=$( echo $Previous|awk -F'/' '{printf("%s/%s",$2,$3)}' )
				    if [ $netmaskGateway != $PreviousNetmaskGateway ]; then
				        if [ $ipPerSegment -lt $ConfNum ]; then
			                echo 'The number of IPs in the same network segment must be equal!'
							echo 'It is recommended that each line configure at least the number of IPs required by each os to reduce the need for more network segments'
				            exit 1
			            fi
						ipNumInOneSegment=$ipPerSegment
						let "segmentNum+=1"
			            ipPerSegment=0
				    fi
					DeviceIpArray[$idx]="${line}"
				    let "idx+=1"
					let "ipPerSegment+=1"
				else
				    DeviceIpArray[$idx]="${line}"
				    let "idx+=1"
					let "ipPerSegment+=1"
				fi
			else
				echo 'Device Ip is illegal'
				exit 1
			fi
		done < $DeviceIp
	else
		echo 'The format of Device ip list is improper!!!'
		exit 1
	fi
else
	echo 'File is not readable or other error!'
	exit 1
fi

# 分发IP并保存分配结果到本地文件
declare -a ResArray
idx=0
NumOsIp=${#OsIpArray[@]}
AllConfNum=$(($ConfNum*$NumOsIp))
NumDeviceIp=${#DeviceIpArray[@]}
if [ $NumOsIp -gt 0 -a $NumDeviceIp -ge $AllConfNum ]; then
    declare -a TempDevice
	idxTemp=0

	if [ $machineType -eq 1 -o $machineType -eq 2 ]; then
	    if [ $workMode == 'SMP' ];then
		    #判断网段数是否合规,每个deviceOS上需要4个不同网段
		    if [ $(($segmentNum % 4)) -ne 0 ];then
			    echo "The number of network segments is illegal and must be an integer multiple of the number of IPs required by each device OS."
				exit 1
			fi
		    OsIdx=0
			for Osip in ${OsIpArray[@]}
			do
			    #每个deviceOS上需要4个不同网段的IP，所以每4行截取一列来配置一个device
			    rowIdx=$(($OsIdx / 4 * 4))
				if [ $(($OsIdx % 4)) -ne 0 ];then
				    continue
				fi
				for columnIdx in $(seq 0 $(($ipNumInOneSegment-1)))
				do
				    tempLine=''
					for Idx in $(seq 0 3)
					do 
					    tempLine="$tempLine"${DeviceIpArray[$((($rowIdx+$Idx)*$ipNumInOneSegment+$columnIdx))]}","
					done
                    tempDevice[$idxTemp]=$tempLine
					let 'idxTemp+=1'
				done
				let 'OsIdx+=1'
			done
		elif [ $workMode == 'AMP' ];then
		    idxTempEnd=$(($NumDeviceIp / 4))  # 需要判断IP数量能否被4整除吗？？待确定。在前面加对device IP网段数的判断就可以省略。
		    for columnIdx in $(seq 0 $(($idxTempEnd-1)))
			do
			    tempLine=''
				for Idx in $(seq 0 3)
				do
				    tempLine="$tempLine"${DeviceIpArray[$(($columnIdx*4+$Idx))]}","
				done
			    tempDevice[$idxTemp]=$tempLine
				let 'idxTemp+=1'
			done
		else
		    echo "Incorrect work mode!"
			exit 1
		fi
		if [ $machineType -eq 1 ];then
		    OsIdx=0
			for osIp in ${OsIpArray[@]}
			do
			    ResArray[$OsIdx]=$osIp";"${tempDevice[$(($OsIdx*2))]}""${tempDevice[$(($OsIdx*2+1))]}
				let 'OsIdx+=1'
			done
		elif [ $machineType -eq 2 ];then
		    OsIdx=0
			for osIp in ${OsIpArray[@]}
			do
			    ResArray[$OsIdx]=$osIp";"${tempDevice[$OsIdx]}
				let 'OsIdx+=1'
			done
		fi
	elif [ $machineType -eq 3 ]; then
	    if [ $(($segmentNum % $IpPerStdCard)) -ne 0 ];then
		    echo "The number of network segments is illegal and must be an integer multiple of the number of IPs required by each device OS."
			exit 1
		fi
	    OsIdx=0
		for Osip in ${OsIpArray[@]}
		do
		    #每个deviceOS上需要个$IpPerStdCard不同网段的IP，所以每$IpPerStdCard行截取一列来配置一个device
		    rowIdx=$(($OsIdx / $IpPerStdCard * $IpPerStdCard))
			if [ $(($OsIdx % $IpPerStdCard)) -ne 0 ];then
			    continue
			fi
			for columnIdx in $(seq 0 $(($ipNumInOneSegment-1)))
			do
			    tempLine=''
				for Idx in $(seq 0 $(($IpPerStdCard-1)))
				do 
				    tempLine="$tempLine"${DeviceIpArray[$((($rowIdx+$Idx)*$ipNumInOneSegment+$columnIdx))]}","
				done
                tempDevice[$idxTemp]=$tempLine
				let 'idxTemp+=1'
			done
			let 'OsIdx+=1'
		done
		if [ $standardCardNum -eq 2 ];then
		    OsIdx=0
			for osIp in ${OsIpArray[@]}
			do
			    ResArray[$OsIdx]=$osIp";"${tempDevice[$(($OsIdx*2))]}""${tempDevice[$(($OsIdx*2+1))]}
				let 'OsIdx+=1'
			done
		elif [ $standardCardNum -eq 1 ];then
		    OsIdx=0
			for osIp in ${OsIpArray[@]}
			do
			    ResArray[$OsIdx]=$osIp";"${tempDevice[$OsIdx]}
				let 'OsIdx+=1'
			done
		fi
	else
	    echo "Incorrect device type parameter!"
		exit 1
	fi
	
	if [ -f "$resultFile" ]; then
	    mv $resultFile $resultFile".bak" 
	fi
	for res in ${ResArray[@]}
	do
		echo $res >> $resultFile
	done
else
    echo "The number of OsIp or DeviceIp is incorrect!!!"
	exit 1
fi

# 获取本机IP和npu id并执行IP配置
localIp=`ip a | grep inet | grep -E -v 'inet6|127.0.0.1|docker|flannel|cni0' | sed 's/^[ \t]*//g' | cut -d ' ' -f2|cut -d '/' -f1|head -1`
matched=0
for res in ${ResArray[@]}
do
    osip=$(echo $res|awk -F';' '{print $1}')
	if [ "$localIp" == "$osip" ]; then
	    isInstalledTool=`npu-smi info`
	    if [ $? != 0 ];then
		    echo "npu-smi tool is not installed, please check it."
			exit 1 
		fi
	    declare -a npuArray
		npuIdx=0
		npuInfo=`npu-smi info|grep -E '910|310'|awk -F' ' '{print $2}'`
		for line in $npuInfo
        do
            npuArray[$npuIdx]="$line"
            let npuIdx++
        done
		if [ "$ConfNum" != "$npuIdx" ]; then
		    echo "The config amount of device ip does not match the actual npu amount."
			exit 1
		fi
		
	    counter=0
        echo $res|awk -F';' '{print $2}'|awk -F',' '{for(i=1;i<NF;i++){print $i;}}'| while read line
    	do
    	    devIp=$(echo $line|awk -F'/' '{print $1}')
    		netmask=$(echo $line|awk -F'/' '{print $2}')
			gateway=$(echo $line|awk -F'/' '{print $3}')
			# 执行本机 device ip 分配
    		echo "hccn_tool -i ${npuArray[$counter]} -ip -s address $devIp netmask $netmask"
			hccn_tool -i ${npuArray[$counter]} -ip -s address $devIp netmask $netmask
    		if [ $? != 0 ]; then
    		    echo "Set ip on device ${npuArray[$counter]} failed, exit!"
    			exit 1
    		fi
			if [ -n "$gateway" ];then
			    # 执行本机 device gateway 分配
    		    echo "hccn_tool -i ${npuArray[$counter]} -gateway -s gateway $gateway"
			    hccn_tool -i ${npuArray[$counter]} -gateway -s gateway $gateway
    		    if [ $? != 0 ]; then
    		        echo "Set gateway on device ${npuArray[$counter]} failed, exit!"
    		    	exit 1
    		    fi
			fi
    		let "counter+=1"
    	done 
    	let "matched+=1"
	fi
 
done
if [ $matched -eq 0 ]; then
    echo 'The local IP does not exist in the assigned file or other error occured, Unexecuted the command "hccn_tool"!'
	exit 1
fi

