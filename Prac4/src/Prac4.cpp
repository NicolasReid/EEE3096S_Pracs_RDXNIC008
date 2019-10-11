/*
 * Prac4.cpp
 *
 * Originall written by Stefan Schröder and Dillion Heald
 *
 * Adapted for EEE3096S 2019 by Keegan Crankshaw
 *
 * Further Edits by Nicolas Reid (RDXNIC008) and Mathew Hayes (HYSMAT002)
 *
 * This file is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 */

#include "Prac4.h"

using namespace std;

bool playing = true; // should be set false when paused
bool stopped = false; // If set to true, program should close
unsigned char buffer[2][BUFFER_SIZE][2];
int buffer_location = 0;
bool bufferReading = 0; //using this to switch between column 0 and 1 - the first column
bool threadReady = false; //using this to finish writing the first column at the start of the song, before the column is played
long lastInterruptTime = 0; //Used for button debounce

// Interrupt configuration
void play_pause_isr(void){
    long interruptTime = millis(); // Debounce timer
    if (interruptTime - lastInterruptTime>200){ //Run, provided that interrupt hasn't been triggured less than 200ms ago
        // Indicate play/pause status
        playing = !playing;
        if(playing){
            printf("Playing\n");
        }else{
            printf("Paused\n");
       }
    }
    lastInterruptTime = interruptTime;
}

void stop_isr(void){
    long interruptTime = millis(); // Debonce timer
    if (interruptTime - lastInterruptTime > 200){ //Run, provided that interrupt hasn't been triggured less than 200ms ago
        // Indicate stop status
        stopped = !stopped;
        printf("Stop Playing\n");
    }
    lastInterruptTime = interruptTime;
    // Exit program
    exit(0);
}

/*
 * Setup Function. Called once
 */
int setup_gpio(void){
    // Set up wiring Pi
    wiringPiSetup();
    // Setting up the buttons
    pinMode(PLAY_BUTTON, INPUT);
    pinMode(STOP_BUTTON, INPUT);
    // Add pull up resistors
    pullUpDnControl(PLAY_BUTTON, PUD_UP);
    pullUpDnControl(STOP_BUTTON, PUD_UP);
    // Attach interrupts to Buttons
    wiringPiISR(PLAY_BUTTON, INT_EDGE_FALLING, &play_pause_isr);
    wiringPiISR(STOP_BUTTON, INT_EDGE_FALLING, &stop_isr);
    // Setting up the SPI interface
    wiringPiSPISetup(SPI_CHAN, SPI_SPEED);
    printf("Set up compleated :)\n");
    return 0;
}


// SPI write thread
void *playThread(void *threadargs){

    // If the thread isn't ready, don't do anything
    while(!threadReady)
        continue;
    // Only play if the stopped flag is false
    while(!stopped){
        // Suspend playing if paused
	    if(!playing)
            // Do nothing (exit function)
            continue;

        // Write the buffer out to SPI
        wiringPiSPIDataRW (SPI_CHAN, buffer[bufferReading][buffer_location] , 2);

        // Check if buffers need to toggle
        buffer_location++;
        if(buffer_location >= BUFFER_SIZE) {
            buffer_location = 0;
            // Switch column once it finishes one column
            bufferReading = !bufferReading;
        }
    }
    pthread_exit(NULL);
}

int main(){

    // Call the setup GPIO function
	if(setup_gpio()==-1){
        return 0;
    }

    // Initialize thread with parameters
    pthread_attr_t tattr;
    pthread_t thread_id;
    // Ceate the variable to set the play thread to have a 99 priority
    int newprio = 99;
    sched_param param;

    pthread_attr_init (&tattr);
    pthread_attr_getschedparam (&tattr, &param); // Safe to get existing scheduling param
    param.sched_priority = newprio; // Set the priority; others are unchanged
    pthread_attr_setschedparam (&tattr, &param); // Setting the new scheduling param
    pthread_create(&thread_id, &tattr, playThread, (void *)1); // New priority specified


    // Open the file
    char ch;
    FILE *filePointer;
    printf("%s\n", FILENAME);
    filePointer = fopen(FILENAME, "r"); // Read mode

    // Notification if there is an error while reading the file
    if (filePointer == NULL) {
        perror("Error while opening the file.\n");
        exit(EXIT_FAILURE);
    }

    int counter = 0;
    int bufferWriting = 0;

    // Read characters from the file
	 while((ch = fgetc(filePointer)) != EOF){
        while(threadReady && bufferWriting==bufferReading && counter==0){
            // Waits in here after it has written to a side, and the thread is still reading from the other side
            continue;
        }

        // Set config and data bits for first 8-bit packet
        char first8 = (ch >> 6); // Assign data bits
        first8 |= 0b00110000; // Add configuration bits
        buffer[bufferWriting][counter][0] = first8; // Store packet in buffer

        // Similarly set next 8 bit packet
        char second8 = ch;
        second8 &= 0b00111111;
        second8 <<= 2;
        buffer[bufferWriting][counter][1] = second8;

        counter++;
        if(counter >= BUFFER_SIZE+1){
            if(!threadReady){
                threadReady = true;
            }

            counter = 0;
            bufferWriting = (bufferWriting+1)%2;
        }

    }

    // Close the file
    fclose(filePointer);
    printf("Complete reading");

    //Join and exit the playthread
    pthread_join(thread_id, NULL);
    pthread_exit(NULL);

    return 0;
}

