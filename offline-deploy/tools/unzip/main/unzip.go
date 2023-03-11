package main

import (
	"archive/zip"
	"errors"
	"fmt"
	"io"
	"log"
	"os"
	"path/filepath"
)

func isDirExists(path string) bool {
	_, err := os.Stat(path) //os.Stat获取文件信息
	if os.IsNotExist(err) {
		return false
	}
	return true
}

func CreateDir(path string) error {
	err := os.Mkdir(path, os.ModePerm)
	if err != nil {
		fmt.Printf("创建目录异常 -> %v\n", err)
		return err
	}
	return nil
}

func isDir(path string) bool {
	s, err := os.Stat(path)
	if err != nil {
		return false

	}
	return s.IsDir()
}

func main() {
	zipReader, _ := zip.OpenReader(os.Args[1])
	for _, file := range zipReader.Reader.File {
		zipFile, err := file.Open()
		if err != nil {
			log.Fatal(err)
		}
		defer zipFile.Close()
		targetDir := os.Args[2]
		extractedFilePath := filepath.Join(
			targetDir,
			file.Name,
		)
		if !isDirExists(targetDir) {
			if err := CreateDir(targetDir); err != nil {
				log.Fatal(errors.New("create dir failed"))
				return
			}
		}
		if dir := isDir(targetDir); !dir {
			log.Fatal(errors.New("targetDir is not dir"))
			return
		}

		if file.FileInfo().IsDir() {
			os.MkdirAll(extractedFilePath, file.Mode())
		} else {
			outputFile, err := os.OpenFile(
				extractedFilePath,
				os.O_WRONLY|os.O_CREATE|os.O_TRUNC,
				file.Mode(),
			)
			if err != nil {
				log.Fatal(err)
			}
			defer outputFile.Close()

			_, err = io.Copy(outputFile, zipFile)
			if err != nil {
				log.Fatal(err)
			}
		}
	}
}
