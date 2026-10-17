
void FUN_00294790(void)

{
  undefined4 uVar1;
  uint uVar2;
  long lVar3;
  uint uVar4;
  long lVar5;
  ulong uVar6;
  long lVar7;
  undefined8 local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  lVar3 = FUN_000f2280(&DAT_02653260);
  if (lVar3 != 0) {
    lVar7 = 0;
    do {
      lVar5 = lVar3;
      lVar3 = FUN_00058050(lVar5);
      FUN_000f2150(lVar5,lVar7);
      lVar7 = lVar5;
    } while (lVar3 != 0);
    do {
      uVar1 = *(undefined4 *)(lVar5 + 8);
      if (*(long *)(lVar5 + 0xc) == 0) {
        local_40 = 0;
        if (DAT_026534e0 != 0) {
          uVar6 = 0;
          uVar2 = DAT_026534e0;
          do {
            if (((&DAT_026532b0)[uVar6 * 3] & 1L << ((byte)uVar1 & 0x3f)) != 0) {
              (*(code *)(&DAT_026532a0)[uVar6 * 3])((&DAT_026532a8)[uVar6 * 3],uVar1,&local_40);
              uVar2 = DAT_026534e0;
            }
            uVar4 = (int)uVar6 + 1;
            uVar6 = (ulong)uVar4;
          } while (uVar4 < uVar2);
        }
      }
      else if (DAT_026534e0 != 0) {
        uVar6 = 0;
        uVar2 = DAT_026534e0;
        do {
          if (((&DAT_026532b0)[uVar6 * 3] & 1L << ((byte)uVar1 & 0x3f)) != 0) {
            (*(code *)(&DAT_026532a0)[uVar6 * 3])((&DAT_026532a8)[uVar6 * 3],uVar1,lVar5 + 0xc);
            uVar2 = DAT_026534e0;
          }
          uVar4 = (int)uVar6 + 1;
          uVar6 = (ulong)uVar4;
        } while (uVar4 < uVar2);
      }
      lVar3 = FUN_00058050(lVar5);
      FUN_000f2160(&DAT_02653270,lVar5);
      lVar5 = lVar3;
    } while (lVar3 != 0);
  }
  FUN_00295460();
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

