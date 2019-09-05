#include "Prac2.h"

extern float data [SAMPLE_COUNT];
extern float carrier[SAMPLE_COUNT];

float result [SAMPLE_COUNT];

FILE * fp; //mod
FILE * fpAcc; //mod

float err = 0.000001; //mod

int main(int argc, char**argv){
    fp = fopen("../data/fpu.csv", "a+");
    fpAcc = fopen("../data/accData.csv","r+");
    printf("Running Unthreaded Test\n");
    printf("Precision sizeof %d\n", sizeof(float));

    tic(); // start the timer
    for (int i = 0;i<SAMPLE_COUNT;i++ ){
        result[i] = data[i] * carrier[i];
    }
    double t = toc();
    //--------------mod---------------
	// Accuracy check:
        long diff = 0;
        float correct_result = 0;
        for (int j = 0; j < SAMPLE_COUNT; j++) {
            fscanf(fpAcc, "%f,", &correct_result);
            if(abs(correct_result-result[j]) > err) {
            diff += 1;
       	    }
         }

    fprintf(fp, "%f,%f,%d\n",t/1e-3, err, diff);
    //------------end mod-------------
    printf("Time: %lf ms\n",t/1e-3);
    printf("End Unthreaded Test\n");
    fclose(fp); fclose(fpAcc);
    return 0;
}
