
void FUN_00926600(uint param_1)

{
  byte bVar1;
  byte bVar2;
  char cVar3;
  byte bVar4;
  long lVar5;
  long lVar6;
  undefined4 uVar7;
  undefined4 uVar8;
  
  if ((param_1 < 4) && (lVar5 = FUN_009496e0(param_1), lVar5 != 0)) {
    lVar6 = FUN_00526f80();
    uVar7 = DAT_0166b890;
    uVar8 = DAT_0166b894;
    if (lVar6 != 0) {
      uVar7 = *(undefined4 *)(lVar6 + 0x144 + (long)*(char *)(lVar5 + 0x13) * 8);
      uVar8 = *(undefined4 *)(lVar6 + 0x140 + (long)*(char *)(lVar5 + 0x13) * 8);
    }
    bVar1 = *(byte *)(lVar5 + 0x1f);
    bVar2 = *(byte *)(lVar5 + 0x1e);
    cVar3 = *(char *)(lVar5 + 0x12);
    bVar4 = *(byte *)(lVar5 + 0x20);
    lVar5 = (long)(int)param_1;
    (&DAT_0273eff0)[lVar5 * 0xc0] = 0x25;
    (&DAT_0273f004)[lVar5 * 0xc0] = 0x25;
    (&DAT_0273f018)[lVar5 * 0xc0] = 0x25;
    (&DAT_0273f02c)[lVar5 * 0xc0] = 0x25;
    (&DAT_0273f040)[lVar5 * 0xc0] = 0x25;
    (&DAT_0273f054)[lVar5 * 0xc0] = 0x25;
    (&DAT_0273f068)[lVar5 * 0xc0] = 0x25;
    (&DAT_0273f07c)[lVar5 * 0xc0] = 0x25;
    (&DAT_0273f090)[lVar5 * 0xc0] = 0x25;
    (&DAT_0273f0a4)[lVar5 * 0xc0] = 0x25;
    (&DAT_0273f0b8)[lVar5 * 0xc0] = 0x25;
    (&DAT_0273f0cc)[lVar5 * 0xc0] = 0x25;
    (&DAT_0273f0e0)[lVar5 * 0xc0] = 0x25;
    (&DAT_0273f0f4)[lVar5 * 0xc0] = 0x25;
    (&DAT_0273f108)[lVar5 * 0xc0] = 0x25;
    (&DAT_0273f11c)[lVar5 * 0xc0] = 0x25;
    (&DAT_0273f130)[lVar5 * 0xc0] = 0x25;
    (&DAT_0273f144)[lVar5 * 0xc0] = 0x25;
    (&DAT_0273f158)[lVar5 * 0xc0] = 0x25;
    (&DAT_0273f16c)[lVar5 * 0xc0] = 0x25;
    (&DAT_0273f180)[lVar5 * 0xc0] = 0x25;
    (&DAT_0273ed40)[lVar5 * 0x2a] = uVar7;
    (&DAT_0273ed44)[lVar5 * 0x2a] = uVar8;
    (&DAT_0273ed48)[lVar5 * 0x2a] = 10;
    (&DAT_0273ed4c)[lVar5 * 0x2a] = 0xb;
    (&DAT_0273ed50)[lVar5 * 0x2a] = 0xd;
    (&DAT_0273ed54)[lVar5 * 0x2a] = 0xc;
    (&DAT_0273ed58)[lVar5 * 0x2a] = 0xf;
    (&DAT_0273ed5c)[lVar5 * 0x2a] = 0xe;
    (&DAT_0273ed60)[lVar5 * 0x2a] = 0;
    (&DAT_0273ed64)[lVar5 * 0x2a] = 1;
    (&DAT_0273ed68)[lVar5 * 0x2a] = 8;
    (&DAT_0273ed6c)[lVar5 * 0x2a] = 9;
    (&DAT_0273ed70)[lVar5 * 0x2a] = 0;
    (&DAT_0273ed74)[lVar5 * 0x2a] = 0xb;
    (&DAT_0273ed78)[lVar5 * 0x2a] = 0xb;
    (&DAT_0273ed7c)[lVar5 * 0x2a] = 2;
    (&DAT_0273ed80)[lVar5 * 0x2a] = 6;
    (&DAT_0273ed84)[lVar5 * 0x2a] = 7;
    (&DAT_0273ed88)[lVar5 * 0x2a] = 4;
    (&DAT_0273ed8c)[lVar5 * 0x2a] = 5;
    (&DAT_0273ed90)[lVar5 * 0x2a] = 4;
    (&DAT_0273ed94)[lVar5 * 0x2a] = 10;
    (&DAT_0273ed98)[lVar5 * 0x2a] = 0xb;
    (&DAT_0273ed9c)[lVar5 * 0x2a] = 3;
    (&DAT_0273eda0)[lVar5 * 0x2a] = 2;
    (&DAT_0273eda4)[lVar5 * 0x2a] = 4;
    (&DAT_0273eda8)[lVar5 * 0x2a] = 5;
    (&DAT_0273edac)[lVar5 * 0x2a] = 0xf;
    (&DAT_0273edb0)[lVar5 * 0x2a] = 0xe;
    (&DAT_0273edb4)[lVar5 * 0x2a] = 2;
    (&DAT_0273edb8)[lVar5 * 0x2a] = 0xd;
    (&DAT_0273edbc)[lVar5 * 0x2a] = 2;
    (&DAT_0273edc0)[lVar5 * 0x2a] = 3;
    (&DAT_0273edc4)[lVar5 * 0x2a] = 7;
    (&DAT_0273edc8)[lVar5 * 0x2a] = 4;
    (&DAT_0273edcc)[lVar5 * 0x2a] = 0xc;
    (&DAT_0273edd0)[lVar5 * 0x2a] = 8;
    (&DAT_0273edd4)[lVar5 * 0x2a] = 9;
    (&DAT_0273edd8)[lVar5 * 0x15] =
         (ulong)bVar1 << 0x20 | (ulong)bVar2 << 0x18 | (long)cVar3 & 0xffffU | (ulong)bVar4 << 0x10;
    (&DAT_0273ede0)[lVar5 * 0x2a] = 0x3f800000;
    (&DAT_0273ede4)[lVar5 * 0x2a] = 0x3f800000;
  }
  return;
}

