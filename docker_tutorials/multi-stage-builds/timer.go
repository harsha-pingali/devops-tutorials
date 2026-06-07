package main

import (
	"fmt"
	"time"
)

func printCurrentTimeUTC() {
	currentTime := time.Now().UTC()
	fmt.Println("Current date and time in UTC:", currentTime.Format("2006-01-02 15:04:05"))
}

func main() {
	printCurrentTimeUTC()
}
