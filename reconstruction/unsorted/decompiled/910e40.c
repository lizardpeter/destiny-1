
void FUN_00910e40(long param_1,long param_2)

{
  undefined8 uVar1;
  long lVar2;
  long lVar3;
  ushort uVar4;
  uint uVar5;
  bool bVar6;
  
  lVar3 = *(long *)(PTR_DAT_019b1b78 + 8);
  uVar1 = FUN_000e8680(lVar3,0,0xffffffff);
  thunk_FUN_012aa986(param_2,0,uVar1);
  uVar4 = *(ushort *)(lVar3 + 0x1c) & 0x78;
  bVar6 = uVar4 != 0;
  if (uVar4 != 0) goto LAB_00910eca;
  uVar5 = *(uint *)(lVar3 + 0x20);
  if ((*(ushort *)(lVar3 + 0x1c) & 0x40) != 0) {
    if (param_2 != 0) {
      lVar2 = FUN_000e8a90(lVar3,param_2);
      if (lVar2 != 0) {
        uVar5 = uVar5 | *(uint *)(lVar2 + 0x20) & 0x5488bf;
        goto LAB_00910ec0;
      }
    }
    uVar5 = uVar5 | 0x5488bf;
  }
LAB_00910ec0:
  bVar6 = (uVar5 & 0xc08070) != 0;
LAB_00910eca:
  if (bVar6) {
    FUN_000e6730(lVar3,param_2,0,0xffffffff,0);
  }
  uVar1 = FUN_005494c0();
  lVar3 = FUN_0054b0c0(uVar1);
  FUN_0090ff60(param_1 + 0x14,param_1 + 0x54,0,param_2 + 0xa0);
  FUN_0090ff60(param_1 + 0x34,param_1 + 0x54,0,param_2 + 0x120);
  FUN_0090ff60(param_1 + 0x6c,param_1 + 0xac,0,param_2 + 0xc0);
  FUN_0090ff60(param_1 + 0x8c,param_1 + 0xac,0,param_2 + 0x140);
  FUN_0090ff60(param_1 + 0xc4,param_1 + 0x104,0,param_2 + 0xe0);
  FUN_0090ff60(param_1 + 0xe4,param_1 + 0x104,0,param_2 + 0x160);
  FUN_0090ff60(param_1 + 0x11c,param_1 + 0x15c,0,param_2 + 0x100);
  FUN_0090ff60(param_1 + 0x13c,param_1 + 0x15c,0,param_2 + 0x180);
  lVar2 = (long)*(char *)(lVar3 + 0xb) * 0x40;
  FUN_0090ff60(param_1 + 0x178 + (long)*(char *)(lVar3 + 0xb) * 0x20,param_1 + 0x618 + lVar2,
               param_1 + 0x610 + lVar2,param_2);
  lVar2 = (long)*(char *)(lVar3 + 0xc) * 0x40;
  FUN_0090ff60(param_1 + 0x178 + (long)*(char *)(lVar3 + 0xc) * 0x20,param_1 + 0x618 + lVar2,
               param_1 + 0x610 + lVar2,param_2 + 0x20);
  lVar2 = (long)*(char *)(lVar3 + 0xd) * 0x40;
  FUN_0090ff60(param_1 + 0x178 + (long)*(char *)(lVar3 + 0xd) * 0x20,param_1 + 0x618 + lVar2,
               param_1 + 0x610 + lVar2,param_2 + 0x40);
  lVar2 = (long)*(char *)(lVar3 + 0xe) * 0x40;
  FUN_0090ff60(param_1 + 0x178 + (long)*(char *)(lVar3 + 0xe) * 0x20,param_1 + 0x618 + lVar2,
               param_1 + 0x610 + lVar2,param_2 + 0x60);
  lVar2 = (long)*(char *)(lVar3 + 0xf) * 0x40;
  FUN_0090ff60(param_1 + 0x178 + (long)*(char *)(lVar3 + 0xf) * 0x20,param_1 + 0x618 + lVar2,
               param_1 + 0x610 + lVar2,param_2 + 0x80);
  return;
}

