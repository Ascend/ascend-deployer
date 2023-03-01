package main

import (
	"archive/zip"
	"io"
	"log"
	"os"
	"path/filepath"
)

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