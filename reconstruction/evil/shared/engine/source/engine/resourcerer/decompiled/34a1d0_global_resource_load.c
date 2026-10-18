
void FUN_0034a1d0(long param_1,uint param_2)

{
  long lVar1;
  char cVar2;
  short sVar3;
  uint uVar4;
  long lVar5;
  ulong uVar6;
  long lVar7;
  undefined1 local_138 [256];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  lVar5 = (ulong)(((uint)((int)param_2 >> 0xd) >> 0x12 | 0x3ff) & (int)param_2 >> 0xd) * 0x40;
  lVar7 = *DAT_01a238a0;
  lVar1 = *(long *)(lVar7 + 0x10 + lVar5);
  uVar6 = (ulong)((param_2 & 0x1fff) * *(int *)(lVar7 + 0x30 + lVar5));
  lVar7 = (lVar1 + uVar6) - ((long)*(int *)(lVar7 + 0x34 + lVar5) & *(ulong *)(lVar1 + 8 + uVar6));
  if (*(char *)(lVar7 + 7) == '\x03') goto LAB_0034a558;
  *(undefined1 *)(lVar7 + 7) = 1;
  if (*(char *)(lVar7 + 6) == '\x02') {
    *(int *)(param_1 + 8) = *(int *)(param_1 + 8) + -1;
  }
  else {
    *(int *)(param_1 + 4) = *(int *)(param_1 + 4) + -1;
  }
  cVar2 = *(char *)(lVar7 + 6);
  if (cVar2 != '\x01') {
    if (cVar2 == '\x02') {
      cVar2 = FUN_00300be0();
      if (cVar2 != '\0') {
        cVar2 = FUN_00300b40();
        if (cVar2 == '\0') {
          FUN_00bb1a40(param_2);
          param_1 = param_1 + 0xc050;
          sVar3 = *(short *)(lVar7 + 0x10);
          if (sVar3 != -1) {
            do {
              FUN_00077290(param_1,(short *)(lVar7 + 0x10),sVar3);
              sVar3 = *(short *)(lVar7 + 0x10);
            } while (sVar3 != -1);
          }
          sVar3 = *(short *)(lVar7 + 0x18);
          if (sVar3 != -1) {
            do {
              FUN_00077290(param_1,(short *)(lVar7 + 0x18),sVar3);
              sVar3 = *(short *)(lVar7 + 0x18);
            } while (sVar3 != -1);
          }
          sVar3 = *(short *)(lVar7 + 0x20);
          if (sVar3 != -1) {
            do {
              FUN_00077290(param_1,(short *)(lVar7 + 0x20),sVar3);
              sVar3 = *(short *)(lVar7 + 0x20);
            } while (sVar3 != -1);
          }
          sVar3 = *(short *)(lVar7 + 0x28);
          if (sVar3 != -1) {
            do {
              FUN_00077290(param_1,(short *)(lVar7 + 0x28),sVar3);
              sVar3 = *(short *)(lVar7 + 0x28);
            } while (sVar3 != -1);
          }
          sVar3 = *(short *)(lVar7 + 0x30);
          if (sVar3 != -1) {
            do {
              FUN_00077290(param_1,(short *)(lVar7 + 0x30),sVar3);
              sVar3 = *(short *)(lVar7 + 0x30);
            } while (sVar3 != -1);
          }
          sVar3 = *(short *)(lVar7 + 0x38);
          if (sVar3 != -1) {
            do {
              FUN_00077290(param_1,(short *)(lVar7 + 0x38),sVar3);
              sVar3 = *(short *)(lVar7 + 0x38);
            } while (sVar3 != -1);
          }
          goto LAB_0034a558;
        }
      }
      FUN_010156f0(local_138,lVar7 + 0x44);
      uVar4 = FUN_00349cb0();
      lVar1 = DAT_02693c58;
      if (uVar4 != 0xffffffff) {
        uVar6 = (ulong)((uVar4 & 0x1fff) * DAT_02693c60);
        *(undefined8 *)(uVar6 + 0x10 + DAT_02693c58) = *(undefined8 *)(lVar7 + 0x10);
        *(undefined8 *)(uVar6 + 0x18 + lVar1) = *(undefined8 *)(lVar7 + 0x18);
        *(undefined8 *)(uVar6 + 0x20 + lVar1) = *(undefined8 *)(lVar7 + 0x20);
        *(undefined8 *)(uVar6 + 0x28 + lVar1) = *(undefined8 *)(lVar7 + 0x28);
        *(undefined8 *)(uVar6 + 0x30 + lVar1) = *(undefined8 *)(lVar7 + 0x30);
        *(undefined8 *)(uVar6 + 0x38 + lVar1) = *(undefined8 *)(lVar7 + 0x30);
        *(undefined2 *)(lVar7 + 0x10) = 0xffff;
        *(undefined2 *)(lVar7 + 0x12) = 0xffff;
        *(undefined4 *)(lVar7 + 0x14) = 0;
        *(undefined2 *)(lVar7 + 0x18) = 0xffff;
        *(undefined2 *)(lVar7 + 0x1a) = 0xffff;
        *(undefined4 *)(lVar7 + 0x1c) = 0;
        *(undefined2 *)(lVar7 + 0x20) = 0xffff;
        *(undefined2 *)(lVar7 + 0x22) = 0xffff;
        *(undefined4 *)(lVar7 + 0x24) = 0;
        *(undefined2 *)(lVar7 + 0x28) = 0xffff;
        *(undefined2 *)(lVar7 + 0x2a) = 0xffff;
        *(undefined4 *)(lVar7 + 0x2c) = 0;
        *(undefined2 *)(lVar7 + 0x30) = 0xffff;
        *(undefined2 *)(lVar7 + 0x32) = 0xffff;
        *(undefined4 *)(lVar7 + 0x34) = 0;
        *(undefined2 *)(lVar7 + 0x38) = 0xffff;
        *(undefined2 *)(lVar7 + 0x3a) = 0xffff;
        *(undefined4 *)(lVar7 + 0x3c) = 0;
        *(uint *)(uVar6 + 0xc + lVar1) = param_2;
        *(uint *)(lVar7 + 0xc) = uVar4;
        FUN_0034a1d0(param_1,uVar4);
      }
      goto LAB_0034a558;
    }
    if (cVar2 != '\x03') goto LAB_0034a558;
  }
  FUN_01010ed0(param_1 + 0x14080);
  if (*(uint *)(param_1 + 0x14094) != 0xffffffff) {
    if ((*(char *)((ulong)((*(uint *)(param_1 + 0x14094) & 0x1fff) * DAT_02693c60) + 4 +
                  DAT_02693c58) < *(char *)(lVar7 + 4)) && (DAT_02693c04 == 0)) {
      FUN_000cc750();
      DAT_02693c04 = 2;
    }
  }
LAB_0034a558:
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

