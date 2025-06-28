undefined8 validate_inputs(short param_1,short param_2)

{
  undefined8 uVar1;
  
  if ((param_1 < 0) || (9 < param_1)) {
    puts("\nError: Your input air-con remote ID doesn\'t exist!\n");
    uVar1 = 0;
  }
  else if ((param_2 < 0x14) || (0x1d < param_2)) {
    puts("\nError: Your input temperature is too cold/hot!\n");
    uVar1 = 0;
  }
  else {
    uVar1 = 1;
  }
  return uVar1;
}


void view_aircon_temps(void)

{
  uint local_c;
  
  puts("");
  for (local_c = 0; (int)local_c < 10; local_c = local_c + 1) {
    printf("[ID %d] Remote Temp: %d, Actual Temp: %d\n",(ulong)local_c,
           (ulong)*(uint *)(AIRCON_REMOTE_TEMP + (long)(int)local_c * 4),
           (ulong)*(uint *)(AIRCON_ACTUAL_TEMP + (long)(int)local_c * 4));
  }
  puts("");
  return;
}

void change_aircon_temp(void)

{
  char cVar1;
  long in_FS_OFFSET;
  short local_16;
  short local_14;
  short local_12;
  long local_10;
  
  local_10 = *(long *)(in_FS_OFFSET + 0x28);
  local_16 = 0;
  local_12 = 0;
  local_14 = 0;
  puts("\nWhich air-con remote to use: ");
  __isoc99_scanf(&DAT_0010219f,&local_16);
  local_12 = local_16;
  puts("\nWhat temperature to set to: ");
  __isoc99_scanf(&DAT_0010219f,&local_14);
  cVar1 = validate_inputs((int)local_16,(int)local_14);
  if (cVar1 != '\0') {
    puts("\nChanging temperature on remote ... ");
    *(int *)(AIRCON_REMOTE_TEMP + (long)(int)local_16 * 4) = (int)local_14;
    puts("Updating temperature of air-con ...");
    *(undefined4 *)(AIRCON_ACTUAL_TEMP + (long)(int)local_12 * 4) =
         *(undefined4 *)(AIRCON_REMOTE_TEMP + (long)(int)local_16 * 4);
    cVar1 = aircon_has_same_temps();
    if (cVar1 != '\0') {
                    /* WARNING: Subroutine does not return */
      exit(1);
    }
  }
  if (local_10 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return;
}

void cat_flag(void)

{
  int __fd;
  ssize_t sVar1;
  long in_FS_OFFSET;
  int local_a8;
  undefined1 local_98 [136];
  undefined8 local_10;
  
  local_10 = *(undefined8 *)(in_FS_OFFSET + 0x28);
  for (local_a8 = 0; local_a8 < 10; local_a8 = local_a8 + 1) {
    if (*(int *)(AIRCON_ACTUAL_TEMP + (long)local_a8 * 4) != 0x19) {
      puts("\nError: Not all air-cons are set to 25 degree celsius! I\'m kicking u out!\n");
                    /* WARNING: Subroutine does not return */
      exit(1);
    }
  }
  __fd = open("flag.txt",0);
  if (__fd < 0) {
    perror("Failed to open flag.txt");
                    /* WARNING: Subroutine does not return */
    exit(1);
  }
  sVar1 = read(__fd,local_98,0x7f);
  if (sVar1 < 0) {
    perror("Failed to read flag.txt");
    close(__fd);
                    /* WARNING: Subroutine does not return */
    exit(1);
  }
  local_98[sVar1] = 0;
  printf("\nFlag: %s\n",local_98);
  close(__fd);
                    /* WARNING: Subroutine does not return */
  exit(1);
}

void display_menu(void)

{
  puts("1. Change air-con temp");
  puts("2. View air-con temps");
  puts("3. Get flag\n");
  return;
}


void setup_aircon(void)

{
  int local_c;
  
  for (local_c = 0; local_c < 10; local_c = local_c + 1) {
    *(int *)(AIRCON_REMOTE_TEMP + (long)local_c * 4) = local_c + 0x14;
    *(int *)(AIRCON_ACTUAL_TEMP + (long)local_c * 4) = local_c + 0x14;
  }
  return;
}


void setup(void)

{
  setbuf(stdin,(char *)0x0);
  setbuf(stdout,(char *)0x0);
  setbuf(stderr,(char *)0x0);
  return;
}

void main(void)

{
  long in_FS_OFFSET;
  int local_14;
  undefined8 local_10;
  
  local_10 = *(undefined8 *)(in_FS_OFFSET + 0x28);
  setup();
  setup_aircon();
  do {
    while( true ) {
      while( true ) {
        display_menu();
        printf("> ");
        __isoc99_scanf(&DAT_0010219f,&local_14);
        getchar();
        if (local_14 != 3) break;
        cat_flag();
      }
      if (local_14 < 4) break;
LAB_0010182f:
      printf("\x1b[2J\x1b[H");
    }
    if (local_14 == 1) {
      change_aircon_temp();
    }
    else {
      if (local_14 != 2) goto LAB_0010182f;
      view_aircon_temps();
    }
  } while( true );
}