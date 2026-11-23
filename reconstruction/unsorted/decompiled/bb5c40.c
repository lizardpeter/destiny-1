
void FUN_00bb5c40(long param_1)

{
  long lVar1;
  int iVar2;
  char cVar3;
  long lVar4;
  long local_48;
  undefined1 local_40 [8];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  lVar4 = 0;
  do {
    lVar1 = param_1 + 0x12a78 + lVar4 * 0x18258;
    FUN_00ba2590(lVar1,local_40);
LAB_00bb5ca0:
    cVar3 = FUN_00ba25a0(lVar1,local_40,&local_48);
    if (cVar3 != '\0') {
      if ((((*(int *)(local_48 + 0x70) == 0) && (*(long *)(local_48 + 0x68) != 0)) &&
          (*(char *)(local_48 + 0xa4) == '\0')) && (iVar2 = *(int *)(local_48 + 0x74), iVar2 != 5))
      {
        if (*(char *)(local_48 + 0xa5) == '\0') {
          if (*(char *)(local_48 + 0x45) == '\0') goto LAB_00bb5d13;
          if (iVar2 == 2) goto LAB_00bb5ca0;
          if (iVar2 == 1) {
            if (*(int *)(local_48 + 0x84) == 1) {
              *(int *)(param_1 + 0x70) = *(int *)(param_1 + 0x70) + 1;
              FUN_00bb3280(local_48,2);
            }
            goto LAB_00bb5ca0;
          }
        }
        else {
          if (*(char *)(local_48 + 0x45) != '\0') {
            FUN_00bb6ee0(param_1,local_48);
            goto LAB_00bb5ca0;
          }
LAB_00bb5d13:
          if (iVar2 != 0) goto LAB_00bb5ca0;
        }
        FUN_00bb3280(local_48,1,0xffffffff);
      }
      goto LAB_00bb5ca0;
    }
    lVar4 = lVar4 + 1;
    if ((int)lVar4 == 3) {
      if (*DAT_01a1f100 != local_38) {
        thunk_FUN_012aa7f6();
        return;
      }
      return;
    }
  } while( true );
}

