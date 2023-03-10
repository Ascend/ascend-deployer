package main

import (
	"bufio"
	"context"
	"encoding/csv"
	"encoding/json"
	"flag"
	"fmt"
	"github.com/go-ini/ini"
	"io"
	v1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/tools/clientcmd"
	"log"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"syscall"
)

const (
	masterNode      = "MASTER"
	workerNode      = "WORKER"
	csvFileSuffix   = ".csv"
	FileMode        = 0644
	maxStringLength = 999
	jsonFileSuffix  = ".json"
)

var (
	inventoryFilePath string
	matchAllFlag      = "MATCHALL"
	multiMasterExtra  = "kube-vip"
	sceneOneMustHave  = []string{
		"calico-node",
		"etcd",
		"kube-apiserver",
		"kube-controller-manager",
		"kube-proxy",
		"kube-scheduler",
	}
	sceneOneMasterShouldHaveAtLeastOne = []string{
		"calico-kube-controllers",
		"coredns",
		"hccl-controller",
		"volcano-scheduler",
		"volcano-controllers",
	}
	sceneOneWorker = []string{
		"ascend-device-plugin",
		"calico-node",
		"kube-proxy",
		"noded",
		"npu-exporter",
	}
	sceneTwoShouldHaveAtLeastOne = []string{
		"calico-kube-controllers",
		"coredns",
		"volcano-scheduler",
		"volcano-controllers",
	}
	sceneTwoWorker = []string{
		"ascend-device-plugin",
		"calico-node",
		"kube-proxy",
	}

	// scene 3
	sceneThreeMustHave = []string{
		"calico-kube-controllers",
		"calico-node",
		"coredns",
		"etctd",
		"kube-apiserver",
		"kube-proxy",
		"kube-scheduler",
	}
	sceneThreeWorker = []string{
		"ascend-device-plugin",
		"calico-node",
		"kube-proxy",
	}
	workerExtraComponent = []string{"npu-exporter", "noded"}
	output               string
	format               string
)

type nodeSummary struct {
	Name        string
	Status      string
	RunningPods []string
	FailingPods []string
	MissingPods []string
	Npu         string
	Components  []string
	NodeType    string
}

var totalMasterNodesSummary = map[string]*nodeSummary{}
var totalWorkerNodesSummary = map[string]*nodeSummary{}

func find(slice []string, val string) bool {
	for _, item := range slice {
		if item == val {
			return true
		}
	}
	return false
}

func isDir(path string) bool {
	s, err := os.Stat(path)
	if err != nil {
		return false

	}
	return s.IsDir()
}

func homeDir() string {
	if h := os.Getenv("HOME"); h != "" {
		return h
	}
	return os.Getenv("USERPROFILE")
}

func readNodeList(nodeList []string) []string {
	var ipAddr []string
	for i := 0; i < len(nodeList); i++ {
		var tmpAddr string
		for j := 0; j < len(nodeList[i]); j++ {
			if nodeList[i][j] != ' ' {
				continue
			} else {
				tmpAddr = nodeList[i][:j]
				ipAddr = append(ipAddr, tmpAddr)
				break
			}
		}
	}
	return ipAddr
}
func getIPsFromLine(content []byte, line *bufio.Reader, masterNodeList []string, workerNodeList []string) ([]string, []string) {
	if string(content) == "[master]" {
		for {
			master, _, err := line.ReadLine()
			if err == io.EOF || string(master) == "" {
				break
			}
			config := string(master)
			if config[0] != '#' {
				masterNodeList = append(masterNodeList, config)
			}
		}
	}
	if string(content) == "[worker]" {
		for {
			worker, _, err := line.ReadLine()
			if err == io.EOF || string(worker) == "" {
				break
			}
			config := string(worker)
			if config[0] != '#' {
				workerNodeList = append(workerNodeList, config)
			}
		}
	}
	return masterNodeList, workerNodeList

}

func getIPsFromInventoryFIle(file *os.File, masterNodeList []string, workerNodeList []string) ([]string, []string) {
	line := bufio.NewReader(file)
	for {
		content, _, err := line.ReadLine()
		if err == io.EOF {
			break
		}
		masterNodeList, workerNodeList = getIPsFromLine(content, line, masterNodeList, workerNodeList)
	}
	return masterNodeList, workerNodeList
}

func addInfo2Node(nodes *v1.NodeList) {
	for _, node := range nodes.Items {
		imageNames := ""
		for _, image := range node.Status.Images {
			imageNames += fmt.Sprintf("%v ", shortestWord(image.Names))
		}
		npus := ""
		for name, value := range node.Status.Capacity {
			if strings.Contains(string(name), "huawei.com/Ascend") {
				npus += fmt.Sprintf("%v:%v ", name.String(), value.String())
			}
		}
		for ip, summary := range totalMasterNodesSummary {
			if summary.Name != node.ObjectMeta.Name {
				continue
			}
			target := totalMasterNodesSummary[ip]
			tmpComponents := strings.Split(imageNames, " ")
			sort.Sort(sort.StringSlice(tmpComponents))
			target.Components = tmpComponents[1:]
			target.Npu = npus
		}
		for ip, summary := range totalWorkerNodesSummary {
			if summary.Name != node.ObjectMeta.Name {
				continue
			}
			target := totalWorkerNodesSummary[ip]
			tmpComponents := strings.Split(imageNames, " ")
			sort.Sort(sort.StringSlice(tmpComponents))
			target.Components = tmpComponents[1:]
			target.Npu = npus
		}
	}
}
func shortestWord(s []string) string {
	best, length := "", maxStringLength
	for _, word := range s {
		if len(word) < length {
			best, length = word, len(word)
		}
	}
	return best
}

func getNodeName(masterIPs, workerIPs []string, client kubernetes.Clientset) ([]string, []string) {
	var masterNodeNameForRealIp []string
	var workerNodeNameForRealIp []string
	inventoryFileIPs := make(map[string]bool, 10)
	nodes, err := client.CoreV1().Nodes().List(context.TODO(), metav1.ListOptions{})
	if err != nil {
		return nil, nil
	}
	realIpForMasterNode := readNodeList(masterIPs)
	realIpForWorkerNode := readNodeList(workerIPs)
	for _, value := range realIpForWorkerNode {
		inventoryFileIPs[value] = false
	}
	for _, value := range realIpForWorkerNode {
		inventoryFileIPs[value] = false
	}
	for _, nodeIP := range realIpForMasterNode {
		totalMasterNodesSummary[nodeIP] = &nodeSummary{NodeType: "MasterNode", Status: "Failed"}
		workingNode := totalMasterNodesSummary[nodeIP]
		for _, node := range nodes.Items {
			if node.Status.Addresses[0].Address == nodeIP {
				inventoryFileIPs[nodeIP] = true
				masterNodeNameForRealIp = append(masterNodeNameForRealIp, node.Name)
				workingNode.Name = node.Name
				workingNode.Status = "OK"
			}
		}
	}
	for _, nodeIP := range realIpForWorkerNode {
		totalWorkerNodesSummary[nodeIP] = &nodeSummary{NodeType: "WorkerNode", Status: "Failed"}
		workingNode := totalWorkerNodesSummary[nodeIP]
		for _, node := range nodes.Items {
			if node.Status.Addresses[0].Address == nodeIP {
				inventoryFileIPs[nodeIP] = true
				workerNodeNameForRealIp = append(workerNodeNameForRealIp, node.Name)
				workingNode.Name = node.Name
				workingNode.Status = "OK"
			}
		}
	}
	addInfo2Node(nodes)
	return masterNodeNameForRealIp, workerNodeNameForRealIp
}

// get config from inventory file
func getSceneNum(inventoryFilePath string, client kubernetes.Clientset) map[string][]string {

	var masterNodeList []string
	var workerNodeList []string
	var sceneNum []string
	var extraComponent []string
	var masterExtraComponentTmp []string
	var workerExtraComponentTmp []string
	cconfigMap := make(map[string][]string, 10)
	file, err := os.Open(inventoryFilePath)
	if err != nil {
		return nil
	}
	defer file.Close()
	masterNodeList, workerNodeList = getIPsFromInventoryFIle(file, masterNodeList, workerNodeList)
	masterNodeNameForRealIp, workerNodeNameForRealIp := getNodeName(masterNodeList, workerNodeList, client)
	cconfigMap["MASTER_NODES_NAME"] = masterNodeNameForRealIp
	cconfigMap["WORKER_NODES_NAME"] = workerNodeNameForRealIp
	cfg, err := ini.Load(inventoryFilePath)
	if err != nil {
		log.Fatal("Failed to read file", err)
	}
	sceneNum = append(sceneNum, cfg.Section("all:vars").Key("SCENE_NUM").String())
	cconfigMap["SCENE_NUM"] = sceneNum
	extraComponent = strings.Split(cfg.Section("all:vars").Key("EXTRA_COMPONENT").String(), ",")
	for _, value := range extraComponent {
		if value == "hccl-controller" {
			masterExtraComponentTmp = append(masterExtraComponentTmp, value)
		}
	}
	cconfigMap["MASTER_EXTRA_COMPONENT"] = masterExtraComponentTmp
	for _, value := range extraComponent {
		if find(workerExtraComponent, value) {
			workerExtraComponentTmp = append(workerExtraComponentTmp, value)
		}
	}
	cconfigMap["WORKER_EXTRA_COMPONENT"] = workerExtraComponentTmp
	return cconfigMap
}

func initkubeConfig() *kubernetes.Clientset {
	var kubeconfig *string
	if home := homeDir(); home != "" {
		kubeconfig = flag.String("kubeconfig", filepath.Join(home, ".kube", "config"), "optional absolute path to config file ")
	} else {
		kubeconfig = flag.String("kubeconfig", "", "absolute path to config file")
	}
	flag.Parse()
	config, err := clientcmd.BuildConfigFromFlags("", *kubeconfig)
	if err != nil {
		return nil
	}
	client, err := kubernetes.NewForConfig(config)
	if err != nil {
		return nil
	}
	return client
}

func GetPodStatus(pod *v1.Pod) string {
	for _, cond := range pod.Status.Conditions {
		if string(cond.Type) == ContainersReady {
			if string(cond.Status) != ConditionTrue {
				return "Unavailable"
			}
		} else if string(cond.Type) == PodInitialized && string(cond.Status) != ConditionTrue {
			return "Initializing"
		} else if string(cond.Type) == PodReady {
			if string(cond.Status) != ConditionTrue {
				return "Unavailable"
			}
			for _, containerState := range pod.Status.ContainerStatuses {
				if !containerState.Ready {
					return "Unavailable"
				}
			}
		} else if string(cond.Type) == PodScheduled && string(cond.Status) != ConditionTrue {
			return "Scheduling"
		}
	}
	return string(pod.Status.Phase)
}

func updatePodsSummary(pods *v1.PodList, summary map[string]*nodeSummary) {
	for _, pod := range pods.Items {
		podName := pod.ObjectMeta.Name
		nodeName := pod.Spec.NodeName
		podIsReady := GetPodStatus(&pod)
		for key, vaule := range summary {
			if vaule.Name != nodeName {
				continue
			}
			if podIsReady == "Running" {
				runningPods := summary[key]
				runningPods.RunningPods = append(runningPods.RunningPods, podName)
				continue
			}
			failingPods := summary[key]
			failingPods.FailingPods = append(failingPods.FailingPods, podName)
		}
	}

}

func copyStringSlice(src []string) []string {
	var dst []string
	dst = append(dst, src...)
	return dst
}
func getPodStatus(neededPods []string, pods *v1.PodList, nodeName string) map[string]bool {
	tmpPods := map[string]bool{}
	for _, podName := range neededPods {
		tmpPods[podName] = false
	}
	for _, pod := range pods.Items {
		if pod.Spec.NodeName != nodeName && nodeName != matchAllFlag {
			continue
		}
		for _, podName := range neededPods {
			if strings.Contains(pod.ObjectMeta.Name, podName) && strings.Contains(string(pod.Status.Phase), "Running") {
				tmpPods[podName] = true
			}
		}
	}
	return tmpPods
}

func updateMissingPods(nodeName, missingPodName, nodeType string) {
	summary := totalWorkerNodesSummary
	if nodeType == masterNode {
		summary = totalMasterNodesSummary
	}
	for key, value := range summary {
		if value.Name != nodeName && nodeName != matchAllFlag {
			continue
		}
		failingPods := summary[key]
		failingPods.MissingPods = append(failingPods.MissingPods, missingPodName)
		failingPods.Status = "Failed"
	}
}

func updateRequiredPodStatus(tmpPods map[string]bool, nodeName, nodeType string) {
	for podName, value := range tmpPods {
		if value == false {
			updateMissingPods(nodeName, podName, nodeType)
		}
	}
}

func checkAllMasterNode(inventoryInfo map[string][]string, pods *v1.PodList,
	mustHave []string, shouldHaveOne []string) {
	for _, masterNode := range inventoryInfo["MASTER_NODES_NAME"] {
		neededPods := copyStringSlice(mustHave)
		tmpPods := getPodStatus(neededPods, pods, masterNode)
		updateRequiredPodStatus(tmpPods, masterNode, masterNode)
	}
	if len(inventoryInfo["MASTER_NODES_NAME"]) > 1 {
		tmpPods := getPodStatus([]string{multiMasterExtra}, pods, matchAllFlag)
		updateRequiredPodStatus(tmpPods, matchAllFlag, masterNode)
	}
	neededPods := copyStringSlice(shouldHaveOne)
	tmpPods := getPodStatus(neededPods, pods, matchAllFlag)
	updateRequiredPodStatus(tmpPods, matchAllFlag, masterNode)
}

func checkMasterNode(inventoryInfo map[string][]string, client kubernetes.Clientset) bool {
	pods, err := client.CoreV1().Pods("").List(context.TODO(), metav1.ListOptions{})
	if err != nil {
		return false
	}
	updatePodsSummary(pods, totalMasterNodesSummary)
	if len(inventoryInfo["SCENE_NUM"]) < 1 {
		return false
	}
	if inventoryInfo["SCENE_NUM"][0] == "1" {
		shouldHaveOne := sceneOneMasterShouldHaveAtLeastOne
		mustHave := sceneOneMustHave
		checkAllMasterNode(inventoryInfo, pods, mustHave, shouldHaveOne)
	}
	if inventoryInfo["SCENE_NUM"][0] == "2" {
		mustHave := sceneOneMustHave
		shouldHaveOne := copyStringSlice(sceneTwoShouldHaveAtLeastOne)
		for _, value := range inventoryInfo["MASTER_EXTRA_COMPONENT"] {
			shouldHaveOne = append(shouldHaveOne, value)
		}
		checkAllMasterNode(inventoryInfo, pods, mustHave, shouldHaveOne)
	}
	if inventoryInfo["SCENE_NUM"][0] == "3" {
		mustHave := sceneThreeMustHave
		checkAllMasterNode(inventoryInfo, pods, mustHave, []string{})
	}
	return true
}

func checkWorkerNode(inventoryInfo map[string][]string, client kubernetes.Clientset) bool {
	pods, err := client.CoreV1().Pods("").List(context.TODO(), metav1.ListOptions{})
	if err != nil {
		return false
	}
	updatePodsSummary(pods, totalWorkerNodesSummary)
	if inventoryInfo["SCENE_NUM"][0] == "1" {
		for _, worker := range inventoryInfo["WORKER_NODES_NAME"] {
			tmpPods := getPodStatus(sceneOneWorker, pods, worker)
			updateRequiredPodStatus(tmpPods, worker, workerNode)
		}
	}
	var tmpSceneWorker []string
	if inventoryInfo["SCENE_NUM"][0] == "2" {
		tmpSceneWorker = copyStringSlice(sceneTwoWorker)
	} else if inventoryInfo["SCENE_NUM"][0] == "3" {
		tmpSceneWorker = copyStringSlice(sceneThreeWorker)
	}
	for _, value := range inventoryInfo["WORKER_EXTRA_COMPONENT"] {
		tmpSceneWorker = append(tmpSceneWorker, value)
	}
	for _, worker := range inventoryInfo["WORKER_NODES_NAME"] {
		tmpPods := getPodStatus(tmpSceneWorker, pods, worker)
		updateRequiredPodStatus(tmpPods, worker, workerNode)
	}
	return true
}

func nodeCheck(configs map[string][]string, client *kubernetes.Clientset) bool {
	masterNodeCheck := checkMasterNode(configs, *client)
	if !masterNodeCheck {
		return false
	}
	if len(configs["WORKER_NODES_NAME"]) != 0 {
		workerNodeCheck := checkWorkerNode(configs, *client)
		if !workerNodeCheck {
			return false
		}
	}
	return true
}

func saveRes2File(saveFilePath string, isJson string) bool {
	switch isJson {
	case "csv":
		if err := savRes2Csv(saveFilePath); err != nil {
			fmt.Println("save result to cvs failed")
			return false
		}
	case "json":
		if err := saveRes2Json(saveFilePath); err != nil {
			fmt.Println("save result to json failed")
			return false
		}
	default:
		fmt.Println("invalid format")
		return false
	}
	return true
}

func saveRes2Json(saveFilePath string) error {
	masterData, _ := json.MarshalIndent(&totalMasterNodesSummary, "", "  ")
	workerData, _ := json.MarshalIndent(&totalWorkerNodesSummary, "", "  ")
	filePath := saveFilePath + jsonFileSuffix
	file, err := os.OpenFile(filePath, syscall.O_RDWR|syscall.O_CREAT|syscall.O_TRUNC, FileMode)
	defer file.Close()
	if err != nil {
		return err
	}
	w := csv.NewWriter(file)
	defer w.Flush()
	jsonData := []string{string(masterData), string(workerData)}
	if err = w.Write(jsonData); err != nil {
		fmt.Println("write json data to json file failed")
		return err
	}
	return nil
}

func savRes2Csv(saveFilePath string) error {
	filePath := saveFilePath + csvFileSuffix
	file, err := os.OpenFile(filePath, syscall.O_RDWR|syscall.O_CREAT|syscall.O_TRUNC, FileMode)
	defer file.Close()
	if err != nil {
		return err
	}
	w := csv.NewWriter(file)
	defer w.Flush()
	row := []string{"IP", "nodeName", "status", "OK pods", "Missing pods", "Failed pods", "NPU", "Component", "NodeType"}
	if err := w.Write(row); err != nil {
		return err
	}
	for key, value := range totalMasterNodesSummary {
		runningPods := strings.Join(value.RunningPods, "\n")
		missingPods := strings.Join(value.MissingPods, "\n")
		failingPods := strings.Join(value.FailingPods, "\n")
		components := strings.Join(value.Components, "\n")
		row := []string{key, value.Name, value.Status, runningPods, missingPods, failingPods, value.Npu, components, value.NodeType}
		if err = w.Write(row); err != nil {
			return err
		}
	}
	for key, value := range totalWorkerNodesSummary {
		runningPods := strings.Join(value.RunningPods, "\n")
		missingPods := strings.Join(value.MissingPods, "\n")
		failingPods := strings.Join(value.FailingPods, "\n")
		components := strings.Join(value.Components, "\n")
		row := []string{key, value.Name, value.Status, runningPods, missingPods, failingPods, value.Npu, components, value.NodeType}
		if err = w.Write(row); err != nil {
			return err
		}
	}
	return nil
}

func isDirExists(path string) bool {
	_, err := os.Stat(path)
	if os.IsNotExist(err) {
		return false
	}
	return true
}

func checkNode() bool {
	allNodeNormal := true
	for _, value := range totalMasterNodesSummary {
		if value.Status == "Failed" {
			allNodeNormal = false
		}
	}
	if !allNodeNormal {
		return allNodeNormal
	}
	for _, value := range totalWorkerNodesSummary {
		if value.Status == "Failed" {
			allNodeNormal = false
		}
	}
	return allNodeNormal
}

func main() {
	flag.StringVar(&inventoryFilePath, "inventoryFilePath", "", "inventory file path")
	flag.StringVar(&output, "filePath", "", "path to save report output")
	flag.StringVar(&format, "format", "csv", "format, csv or json")
	flag.Parse()
	if isDir(output) || !isDirExists(output) || isDir(inventoryFilePath) {
		fmt.Println("filePath or inventoryFilePath is invalid, please check it")
		return
	}
	client := initkubeConfig()
	if client == nil {
		fmt.Println("init kube config failed.")
		return
	}
	configs := getSceneNum(inventoryFilePath, *client)
	if nodeChecker := nodeCheck(configs, client); !nodeChecker {
		fmt.Println("check node failed")
		return
	}
	if saveChecker := saveRes2File(output, format); !saveChecker {
		fmt.Println("save nodes data to csv failed")
		return
	}
	if !checkNode() {
		fmt.Println("nodes status is abnormal, please check the output file for detail.")
		return
	}
	fmt.Println("All nodes running normally, for detail please check output file.")

}
