
void FUN_009110d0(long param_1,undefined4 *param_2)

{
  undefined8 uVar1;
  long lVar2;
  long lVar3;
  ushort uVar4;
  uint uVar5;
  bool bVar6;
  
  lVar3 = *(long *)(PTR_DAT_019b1b80 + 8);
  uVar1 = FUN_000e8680(lVar3,0,0xffffffff);
  thunk_FUN_012aa986(param_2,0,uVar1);
  uVar4 = *(ushort *)(lVar3 + 0x1c) & 0x78;
  bVar6 = uVar4 != 0;
  if (uVar4 == 0) {
    uVar5 = *(uint *)(lVar3 + 0x20);
    if ((*(ushort *)(lVar3 + 0x1c) & 0x40) != 0) {
      if ((param_2 == (undefined4 *)0x0) || (lVar2 = FUN_000e8a90(lVar3,param_2), lVar2 == 0)) {
        uVar5 = uVar5 | 0x5488bf;
      }
      else {
        uVar5 = uVar5 | *(uint *)(lVar2 + 0x20) & 0x5488bf;
      }
    }
    bVar6 = (uVar5 & 0xc08070) != 0;
  }
  if (bVar6) {
    FUN_000e6730(lVar3,param_2,0,0xffffffff,0);
  }
  uVar1 = FUN_005494c0();
  lVar3 = FUN_0054b0c0(uVar1);
  if ((long)*(char *)(lVar3 + 0x19) != -1) {
    param_1 = (long)*(char *)(lVar3 + 0x19) * 0x20 + 0x178 + param_1;
    lVar3 = 0;
    do {
      if (7 < (int)lVar3) {
        return;
      }
      *param_2 = *(undefined4 *)(param_1 + lVar3 * 4);
      lVar2 = lVar3 * 4;
      lVar3 = lVar3 + 1;
    } while (*(int *)(param_1 + lVar2) == -1);
  }
  return;
}

