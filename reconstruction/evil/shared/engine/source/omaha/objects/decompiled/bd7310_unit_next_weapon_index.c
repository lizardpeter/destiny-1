
ulong FUN_00bd7310(undefined4 param_1,short param_2,short param_3)

{
  char cVar1;
  ulong uVar2;
  short sVar3;
  short sVar4;
  int iVar5;
  short sVar6;
  undefined1 local_68 [40];
  undefined1 local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  iVar5 = 0;
  if (param_2 != -1) {
    iVar5 = param_2 + 4 + (int)param_3;
    iVar5 = iVar5 - (((uint)(iVar5 >> 0x1f) >> 0x1e) + 4 + (int)param_2 + (int)param_3 & 0xfffc);
  }
  sVar3 = (short)iVar5;
  sVar6 = -1;
  do {
    sVar4 = (short)iVar5;
    local_40 = 0;
    cVar1 = FUN_00bd51e0(param_1);
    if ((((cVar1 != '\0') && (iVar5 = FUN_00353640(local_68,(int)sVar4), iVar5 != -1)) &&
        (cVar1 = FUN_00bd6a50(param_1,iVar5), cVar1 != '\0')) && (FUN_00bc9af0(iVar5), sVar6 == -1))
    {
      sVar6 = sVar4;
    }
    iVar5 = (int)((int)sVar4 + (param_3 < 0) + 1 + (uint)(param_3 < 0)) % 4;
  } while ((short)iVar5 != sVar3);
  if (*DAT_01a1f100 != local_38) {
    uVar2 = thunk_FUN_012aa7f6();
    return uVar2;
  }
  return (ulong)(uint)(int)sVar6;
}

