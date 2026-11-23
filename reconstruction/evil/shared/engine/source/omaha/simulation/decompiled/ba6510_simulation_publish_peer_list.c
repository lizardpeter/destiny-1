
void FUN_00ba6510(undefined8 *param_1,undefined1 *param_2,undefined4 *param_3)

{
  int iVar1;
  long lVar2;
  
  iVar1 = FUN_00bb58c0(*param_1);
  if (iVar1 == -1) {
    *param_2 = 0;
  }
  else {
    lVar2 = FUN_00bb54d0(*param_1,iVar1);
    *param_2 = 0;
    if ((lVar2 != 0) && (*(char *)(lVar2 + 0xfc) != '\0')) {
      *param_3 = *(undefined4 *)(lVar2 + 0x4c);
      thunk_FUN_012aa7c6(param_3 + 1,lVar2 + 0x5c,0xa0);
      *(undefined4 *)((long)param_1 + 0x12dc) = *(undefined4 *)(lVar2 + 0x4c);
      thunk_FUN_012aa7c6((long)param_1 + 0x12ec,lVar2 + 0x5c,0xa0);
      FUN_00ba65d0(param_1);
      *param_2 = 1;
      *(undefined1 *)(lVar2 + 0xfc) = 0;
    }
  }
  return;
}

