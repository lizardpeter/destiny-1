
long FUN_00088af0(char *param_1,uint param_2,long param_3,int param_4)

{
  undefined *puVar1;
  int iVar2;
  int iVar3;
  long lVar4;
  long lVar5;
  long lVar6;
  bool bVar7;
  char *local_258;
  undefined8 local_250;
  undefined8 local_248;
  undefined8 local_240;
  undefined1 local_238 [256];
  char local_138 [256];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  if ((param_2 & 0x10) == 0) {
    FUN_000886e0(param_1,local_238,0x100);
  }
  else {
    FUN_00065030(local_238,param_1,0x100);
  }
  puVar1 = PTR_DAT_01904b80;
  iVar2 = FUN_00065290(PTR_DAT_01904b80,0x100);
  iVar3 = FUN_00065290(param_1,0x100);
  lVar6 = (long)(iVar3 - iVar2);
  if (iVar3 - iVar2 < 0) {
    lVar6 = 0;
  }
  iVar2 = thunk_FUN_012aab16(puVar1,param_1 + lVar6,(long)iVar2);
  bVar7 = false;
  if (iVar2 != 0) {
    bVar7 = *param_1 != '\0';
  }
  FUN_00088d30(local_238,&local_240,&local_248,&local_250,&local_258,bVar7,0x2f);
  lVar6 = (long)param_4;
  FUN_00065030(param_3,&DAT_012ad038,lVar6);
  if ((param_2 & 1) != 0) {
    FUN_00065030(local_138,local_240,0x100);
    lVar4 = 0;
    do {
      if (local_138[lVar4] == '\\') {
        local_138[lVar4] = '/';
      }
      lVar4 = lVar4 + 1;
    } while ((int)lVar4 != 0x100);
    FUN_00065030(param_3,local_138,lVar6);
  }
  if ((param_2 & 2) != 0) {
    FUN_00088290(param_3,param_4,local_248);
  }
  if ((param_2 & 4) != 0) {
    FUN_00088290(param_3,param_4,local_250);
  }
  if (((param_2 & 8) != 0) && (*local_258 != '\0')) {
    lVar4 = FUN_000650a0(param_3,lVar6);
    lVar5 = thunk_FUN_012aa816(local_258);
    lVar5 = lVar5 + lVar4;
    bVar7 = false;
    if ((0 < lVar4) && (lVar4 < lVar6)) {
      bVar7 = *local_258 != '.';
      lVar5 = (ulong)bVar7 + lVar5;
    }
    if (lVar5 < lVar6) {
      if (bVar7) {
        *(undefined2 *)(param_3 + lVar4) = 0x2e;
        lVar4 = lVar4 + 1;
      }
      FUN_00065030(param_3 + lVar4,local_258,lVar6 - lVar4);
    }
  }
  if (*DAT_01a1f100 != local_38) {
    lVar6 = thunk_FUN_012aa7f6();
    return lVar6;
  }
  return param_3;
}

