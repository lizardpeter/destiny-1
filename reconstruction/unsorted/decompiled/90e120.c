
void FUN_0090e120(char param_1)

{
  long *plVar1;
  char cVar2;
  int iVar3;
  long lVar4;
  int iVar5;
  undefined1 local_a0 [8];
  int local_98;
  long local_90;
  undefined1 local_88 [8];
  int local_80;
  long local_78;
  undefined1 local_70 [8];
  int local_68;
  long local_60;
  undefined1 local_58 [8];
  undefined4 local_50;
  int local_48 [4];
  long local_38;
  
  plVar1 = DAT_01a1f100;
  local_38 = *DAT_01a1f100;
  cVar2 = FUN_00906f70();
  if (cVar2 == '\0') goto LAB_0090e341;
  local_48[2] = -1;
  local_48[0] = -1;
  if (param_1 != '\0') {
    FUN_00074a80(local_58,DAT_0273ea80);
    while (local_60 = FUN_00074a90(local_58), local_60 != 0) {
      FUN_00922ef0(local_50,0xffffffff);
      FUN_00923080(local_50,0xffffffff);
    }
    FUN_00923430(0,0xffffffff);
  }
  FUN_00074a80(local_70,DAT_0273ea80);
  local_78 = 0;
  local_78 = FUN_00074a90(local_70);
  iVar5 = local_48[2];
  while (local_48[2] = iVar5, local_78 != 0) {
    if (*(int *)(local_78 + 0x628) == *(int *)(DAT_0273ea90 + 0xb4)) {
      iVar5 = *(int *)(local_78 + 0x62c);
      local_48[(long)iVar5 + 2] = local_68;
      local_48[iVar5] = *(int *)(local_78 + 0x630);
    }
    local_78 = FUN_00074a90(local_70);
    iVar5 = local_48[2];
  }
  if ((param_1 != '\0') && (iVar5 != -1)) {
    FUN_00922ef0(iVar5,0);
    FUN_00923080(iVar5,local_48[0]);
  }
  cVar2 = FUN_0093d5a0();
  iVar5 = local_48[2];
  if (cVar2 == '\0') {
    if (*(int *)(DAT_0273ea90 + 0xb4) == -1) {
LAB_0090e2ce:
      FUN_00074a80(local_a0,DAT_0273ea80);
      do {
        lVar4 = FUN_00074a90(local_a0);
        if (lVar4 == 0) break;
      } while ((*(byte *)(lVar4 + 0x610) & 2) != 0);
      iVar5 = -1;
      if (lVar4 != 0) {
        iVar5 = local_98;
      }
    }
    else {
      FUN_00074a80(local_88,DAT_0273ea80);
LAB_0090e290:
      do {
        local_90 = FUN_00074a90(local_88);
        if (local_90 != 0) {
          if ((*(byte *)(local_90 + 0x610) & 2) != 0) goto LAB_0090e290;
        }
        if (local_90 == 0) goto LAB_0090e2ce;
      } while (*(int *)(local_90 + 0x628) != *(int *)(DAT_0273ea90 + 0xb4));
      iVar5 = local_80;
      if (local_80 == -1) goto LAB_0090e2ce;
    }
    iVar3 = FUN_00945900(0);
    if ((iVar3 != -1) && (iVar3 = FUN_009236b0(0), iVar3 == -1)) {
      FUN_00923430(0,iVar5);
    }
    iVar3 = FUN_00923770();
    if (iVar3 != 0) goto LAB_0090e341;
  }
  FUN_00923430(0,iVar5);
LAB_0090e341:
  if (*plVar1 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

