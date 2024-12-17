package main

import (
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"os/exec"
	"time"
)

type User struct {
	Name string `json:"name"`
	Age  int    `json:"age"`
}

var updateFilePath string

func main() {
	updateFilePath = os.Args[1]
	if updateFilePath == "" {
		fmt.Println("filePath arg not set")
		os.Exit(1)
	}

	http.HandleFunc("/update", handlePost)

	fmt.Println("Server listening on port 8080...")
	http.ListenAndServe(":8080", nil)
}

func handlePost(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	body, err := ioutil.ReadAll(r.Body)
	if err != nil {
		http.Error(w, "Error reading request body", http.StatusInternalServerError)
		return
	}

	err = os.WriteFile(updateFilePath, body, 0644)
	if err != nil {
		fmt.Printf("Error writing to file: %s\nMessage: %s", updateFilePath, err)
	}

	fmt.Println("Importing cards...")

	output, err := exec.Command("docker", "exec", "nrdb-dev", "bash", "-c", "php bin/console doctrine:schema:update --force; php bin/console app:import:std -f cards").
		Output()
	if err != nil {
		fmt.Println("Error Running docker exec:", err)
		return
	}
	fmt.Println(string(output))

	fmt.Printf("Received update: %s", time.Now().Format("2006-01-02 15:04:05"))

	w.WriteHeader(http.StatusOK)
	w.Write([]byte("Update received"))
}
