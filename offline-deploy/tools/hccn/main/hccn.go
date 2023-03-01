package main

import (
	"bytes"
	"encoding/binary"
	"errors"
	"flag"
	"fmt"
	"net"
	"os"
	"os/exec"
	"strconv"
	"strings"
	"time"
)

const (
	fullNum    = 8
	halfNum    = 4
	startPoint = 2
	argsMin    = 2
	cmdIndex   = 1
	firstNum   = 0
)

var (
	detectIP string
	ip       string
	netMask  string
	mode string
	action string
)

type IP struct {
	ID1 uint8
	ID2 uint8
	ID3 uint8
	ID4 uint8
}

func check(ip string) error {
	if net.ParseIP(ip) == nil || ip == "0.0.0.0" {
		return errors.New("invalid ip")
	}
	return nil
}

func parseIP(ipStr string) (*IP, error) {
	ipBytes := net.ParseIP(ipStr).To4()
	ip := &IP{}
	if err := binary.Read(bytes.NewReader(ipBytes), binary.BigEndian, ip); err != nil {
		return nil, err
	}
	return ip, nil
}

func confIP(ipStr string, mode string, count int) ([]string, error) {
	err := check(ipStr)
	if err != nil {
		return nil, err
	}
	ip, err := parseIP(ipStr)
	ipArray := make([]string, count)
	b0 := int(ip.ID1)
	b1 := int(ip.ID2)
	b2 := int(ip.ID3)
	b3 := int(ip.ID4)
	if mode == "SMP" {
		b31 := b3 + 1
		if count == fullNum {
			b21 := b2
			for i := 0; i < count/2; i++ {
				b2 = b21 + i
				ipArray[i] = strconv.Itoa(b0) + "." + strconv.Itoa(b1) + "." + strconv.Itoa(b2) + "." + strconv.Itoa(b3)
				ipArray[i+count/2] = strconv.Itoa(b0) + "." + strconv.Itoa(b1) + "." + strconv.Itoa(b2) + "." + strconv.Itoa(b31)
			}
		}
	}
	if mode == "AMP" {
		if count == fullNum {
			b31 := b3
			for i := 0; i < count; i++ {
				b3 = b31 + i
				ipArray[i] = strconv.Itoa(b0) + "." + strconv.Itoa(b1) + "." + strconv.Itoa(b2) + "." + strconv.Itoa(b3)
			}
		}
	}
	return ipArray, nil
}

func init() {
	flag.StringVar(&mode, "mode", "default", "working mode")
	flag.StringVar(&ip, "ip", "default", "IP address of the NPU in the environment")
	flag.StringVar(&detectIP, "detectip", "default", "Detect IP address of the NPU in the environment")
	flag.StringVar(&netMask, "netmask", "default", "subnet mask")
}

func execCmd(cmdContent string) error {
	cmd := exec.Command("bash", "-c", cmdContent)
	cmd.Stdout = os.Stdout
	return cmd.Run()
}

func getNpuIDAndNum() (string, string, error) {
	cmdID := exec.Command("bash", "-c", "npu-smi info -l | grep \"NPU ID\" | awk '{print $4}'")
	cmdCount := exec.Command("bash", "-c", "npu-smi info -l | head -n 1 | awk '{print $4}'")
	out, err := cmdID.Output()
	if err != nil {
		return "", "", err
	}
	outNum, err := cmdCount.Output()
	if err != nil {
		return "", "", err
	}
	npuID := string(out)
	npuNum := string(outNum)
	return npuID, npuNum, nil
}

func checkNetStatus(id string) error {
	cmdContent := fmt.Sprintf("hccn_tool -i %s -net_health -g", id)
	if err := execCmd(cmdContent); err != nil {
		fmt.Errorf("Failed to configure the IP address of the NPU whose ID is %s", id)
		return err
	}
	fmt.Sprintf("The IP address of the NPU whose ID is %s is configured successfully", id)
	cmdCheckIP := fmt.Sprintf("hccn_tool -i %s -ip -g", id)
	if err := execCmd(cmdCheckIP); err != nil {
		return err
	}
	cmdCheckNetdetect := fmt.Sprintf("hccn_tool -i %s -netdetect -g", id)
	if err := execCmd(cmdCheckNetdetect); err != nil {
		return err
	}
	return nil
}

func checkNpuIP(id string) error {
	cmdContent := fmt.Sprintf("hccn_tool -i %s -ip -g", id)
	return execCmd(cmdContent)
}

func npuIPConf(id string, ip string, netmask string) error {
	cmdContent := fmt.Sprintf("hccn_tool -i %s -ip -s address %s netmask %s", id, ip, netmask)
	return execCmd(cmdContent)
}

func detectIPConf(id string, ip string) error {
	cmdContent := fmt.Sprintf("hccn_tool -i %s -netdetect -s address %s", id, ip)
	return execCmd(cmdContent)
}

func getIDArrayAndCount() ([]string, int, error) {
	npuID, npuNum, err := getNpuIDAndNum()
	if err != nil {
		return nil, 0, err
	}
	npuIDArray := strings.Split(npuID, string('\n'))
	npuNumArray := strings.Split(npuNum, string('\n'))

	count, err := strconv.Atoi(npuNumArray[0])
	if err != nil {
		return nil, 0, err
	}
	return npuIDArray, count, nil
}

func view(npuIDArray []string, count int) error {
	for i := 0; i < count; i++ {
		if err := checkNetStatus(npuIDArray[i]); err != nil {
			return err
		}
	}
	return nil
}

func config(npuIDArray []string, count int) (err error) {
	if ip == "default" || detectIP == "default" || netMask == "default" {
		fmt.Println("WARNING: the ip, detectip, or netmask is not specified.")
		return
	}
	var ipArray []string
	var detectIPArray []string
	if strings.Contains(ip, ",") || count == 1 {
		ipArray = strings.Split(ip, ",")
		detectIPArray = strings.Split(detectIP, ",")
		for i := 0; i < count; i++ {
			// 配置之前查看npu卡之前是否配置ip
			err := checkNpuIP(npuIDArray[i])
			if err != nil {
				return err
			}
			// 配置npu卡ip
			if err := npuIPConf(npuIDArray[i], ipArray[i], netMask); err != nil {
				return err
			}
			// 配置npu卡对端ip
			if err := detectIPConf(npuIDArray[i], detectIPArray[i]); err != nil {
				return err
			}
		}
	} else {
		ipArray, err = confIP(ip, mode, count)
		if err != nil {
			return err
		}
		detectIPArray, err = confIP(detectIP, mode, count)
		if err != nil {
			return err
		}
		for i := 0; i < count; i++ {
			// 配置之前查看npu卡之前是否配置ip
			err := checkNpuIP(npuIDArray[i])
			if err != nil {
				return err
			}
			// 配置npu卡ip
			if err := npuIPConf(npuIDArray[i], ipArray[i], netMask); err != nil {
				return err
			}
			// 配置npu卡对端ip
			if mode == "AMP" {
				if err := detectIPConf(npuIDArray[i], detectIPArray[firstNum]); err != nil {
					return err
				}
			}
			if mode == "SMP" {
				if err := detectIPConf(npuIDArray[i], detectIPArray[i%halfNum]); err != nil {
					return err
				}
			}
		}
	}

	time.Sleep(5 * time.Second)
	err = view(npuIDArray, count)
	if err != nil {
		return err
	}
	return nil
}

func usage() {
	fmt.Printf("Usage of hccn: \n \n" +
        "-mode       \"working mode\" \n \n" +
	    "-ip         \"IP address of the NPU in the environment\" \n \n" +
	    "-detectip   \"Detect IP address of the NPU in the environment\" \n \n" +
	    "-netmask    \"subnet mask\" \n \n")
}

func parse(npuIDArray []string, count int) error {
	if len(os.Args) < argsMin {
		return errors.New("missing command, type -h or -help for help")
	}
	action := os.Args[cmdIndex]
	err := flag.CommandLine.Parse(os.Args[startPoint:])
	if err != nil {
		return err
	}
	switch action {
	case "config":
		err := config(npuIDArray, count)
		if err != nil {
			return err
		}
	case "view":
		err := view(npuIDArray, count)
		if err != nil {
			return err
		}
	case "-h":
		usage()
	case "--help":
		usage()
	default:
		return errors.New("unknown command, type -h or -help for help")
	}
	return nil
}

func main() {
	npuIDArray, count, err := getIDArrayAndCount()
	if err != nil {
		fmt.Println(err)
		return
	}
	err = parse(npuIDArray, count)
	if err != nil {
		fmt.Println(err)
		return
	}
}
