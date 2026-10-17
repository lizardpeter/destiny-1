
void FUN_007df6e0(long param_1,long param_2)

{
  long lVar1;
  undefined8 uVar2;
  char cVar3;
  byte bVar4;
  uint uVar5;
  undefined4 uVar6;
  int iVar7;
  int iVar8;
  long lVar9;
  int *piVar10;
  uint local_48 [2];
  undefined4 local_40 [2];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  piVar10 = (int *)(param_2 + 0xc0);
  uVar2 = *(undefined8 *)(param_1 + 0x50);
  lVar9 = 0x10;
  do {
    if (*piVar10 == 1) {
      lVar1 = param_2 + lVar9;
      local_48[0] = FUN_00f82b00(lVar1);
      uVar5 = local_48[0] & 0xff;
      if (((uVar5 < 0x17) && (uVar5 != 0)) && ((uVar5 | 2) != 0xf)) {
        cVar3 = FUN_00f7d980(local_48,0);
        if (cVar3 != '\0') {
          cVar3 = FUN_00f7d780(local_48);
          if ((cVar3 != '\0') && ((char)local_48[0] != '\0')) {
            uVar6 = FUN_00057e60(lVar1);
            local_40[0] = FUN_00f82b00(lVar1);
            iVar7 = FUN_00f7d730(local_40);
            iVar8 = FUN_00f82ae0(lVar1);
            bVar4 = FUN_00f826c0(lVar1);
            FUN_00f7fd40(uVar2,uVar6,(uint)((iVar8 * 0x40 + 0x40) * iVar7 << (bVar4 & 0x1f)) >> 8,
                         0x40,0x38,0x2000000,1);
          }
        }
      }
    }
    piVar10 = piVar10 + 1;
    lVar9 = lVar9 + 0x2c;
  } while ((int)lVar9 != 0xc0);
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

