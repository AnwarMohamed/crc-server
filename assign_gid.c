#include <unistd.h>
#include <sys/types.h>
#include <stdio.h>

int main(int argc, char *argv[]) {
    //setreuid(geteuid(), geteuid());
    //setregid(getegid(), getegid());
    int guid;
    int i;
    if (argc<3){
        printf("Error: This commands takes two arguments: guid and command\n");
        return;
    }
    else{
        guid=atoi(argv[1]);
        printf("guid: %d\n",guid);
        printf("command:",argv[2]);
        for (i=2;i<argc;i++){
            printf("%s ",argv[i]);
        }
        printf("\n");
        //setreuid(geteuid(), geteuid());
        setregid(guid, guid);    
        return execv(argv[2], argv+2);
    }
    

}
