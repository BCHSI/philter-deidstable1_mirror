package main

import (
    "log"
    "os"
    "os/exec"
    "os/signal"
    "path/filepath"
    "syscall"
)



func main() {

	searchDir := "data/i2b2_notes/"
	foutpath  := "data/i2b2_results/"

    fileList := []string{}
    filepath.Walk(searchDir, func(path string, f os.FileInfo, err error) error {
        fileList = append(fileList, path)
        return nil
    })

    max_processes := 20 //number of concurrent instances of the script to run at once
    num_files := len(fileList)
    finished := 0
    finish_chan := make(chan string)
    defer close(finish_chan)

    signal_chan := make(chan os.Signal, 1)
    defer close(signal_chan)
	signal.Notify(signal_chan,
		syscall.SIGHUP,
		syscall.SIGINT,
		syscall.SIGTERM,
		syscall.SIGQUIT)


    //kick off our initial processes
    for i, fn := range fileList {
        
        go RunPhilter(fn, foutpath, finish_chan)
        if i == max_processes {
        	break
        }
    }

    //now pop these files from the list of files to complete
    fileList = fileList[max_processes:]
    //keep track of which files have completed processing
    m := map[string]bool{}

    for  {
      select {
      case f := <- finish_chan:
      	finished += 1
      	log.Println(f, finished, num_files)
      	if finished >= len(fileList) {
      		log.Println("finished", finished)
      		return
      	} else {
      		//grab our next item off the filelist and run it
      		fn := fileList[finished]
      		go RunPhilter(fn, foutpath, finish_chan)
      	}
      	//mark this as completed
      	m[f] = true
      case s := <-signal_chan:
      	//received a signal (assume it's kill)
      	log.Println("Signal revd:", s)
      	os.Exit(1)
      	return
      }
    }
	
    log.Println("Philtered TOTAL: ", finished)

}	

//
// Runs our python script
//
func RunPhilter(fn string, foutpath string, finish_chan chan string){
	
	cmd := exec.Command("/usr/local/bin/python3", "philter_file.py", fn, foutpath)
    cmd.Stdout = os.Stdout
    cmd.Stderr = os.Stderr
    cmd.Run()
    finish_chan <- fn
}

