
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_007dd060(long *param_1)

{
  long *plVar1;
  long lVar2;
  long lVar3;
  long lVar4;
  char cVar5;
  uint uVar6;
  undefined4 uVar7;
  long lVar8;
  long lVar9;
  long lVar10;
  undefined8 uVar11;
  long lVar12;
  bool bVar13;
  int iVar14;
  long lVar15;
  int iVar16;
  undefined1 auVar17 [16];
  undefined1 local_78 [16];
  undefined8 local_68;
  long local_60;
  undefined4 local_48;
  undefined4 local_44;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  lVar10 = *param_1;
  if (*(char *)(lVar10 + 0x2d8) != '\0') {
    FUN_000f2c60(*(undefined4 *)(lVar10 + 0x2d4),0);
    lVar10 = *param_1;
  }
  thunk_FUN_012aba56(*(undefined4 *)(lVar10 + 0x80),local_78);
  lVar10 = *param_1;
  if (-1 < local_60) {
    iVar16 = (int)*(undefined8 *)(lVar10 + 0x13410);
    iVar16 = iVar16 - (((uint)((long)*(undefined8 *)(lVar10 + 0x13410) >> 0x3f) >> 0x1d) + iVar16 &
                      0xfffffff8);
    bVar13 = false;
    iVar14 = iVar16;
    do {
      lVar15 = (long)iVar14 * 0x20;
      if ((local_60 == *(long *)(lVar10 + 0x13310 + lVar15)) &&
         (bVar13 = true, *(long *)(lVar10 + 0x13320 + lVar15) == 0)) {
        *(undefined8 *)(lVar10 + 0x13320 + lVar15) = local_68;
        *(undefined4 *)(lVar10 + 0x13328 + lVar15) = local_48;
        *(undefined4 *)(lVar10 + 0x1332c + lVar15) = local_44;
      }
      iVar14 = (iVar14 + 1) - (iVar14 + 1 + ((uint)(iVar14 + 1 >> 0x1f) >> 0x1d) & 0xfffffff8);
    } while ((iVar14 != iVar16) && (!bVar13));
  }
  lVar10 = *param_1;
  uVar6 = *(uint *)(lVar10 + 0x2cc);
  if (0x80000000 < uVar6 - *(int *)(lVar10 + 0x2c8)) {
    do {
      lVar15 = *(long *)(lVar10 + 200 + (ulong)(uVar6 & 0x3f) * 8);
      lVar10 = *param_1;
      if (*(int *)(lVar15 + 0x18) == 0) break;
      *(undefined8 *)(lVar10 + 200 + (ulong)(uVar6 & 0x3f) * 8) = 0;
      *(int *)(*param_1 + 0x2cc) = *(int *)(*param_1 + 0x2cc) + 1;
      while (lVar10 = *param_1, *DAT_026e4860 - *(int *)(lVar10 + 0xbc) < 0) {
        cVar5 = FUN_000fb860();
        if (cVar5 == '\0') {
          thunk_FUN_012ab3b6(300);
        }
      }
      if (*(char *)(lVar15 + 0x28) == '\0') {
        iVar14 = thunk_FUN_012ac5f6(*(undefined4 *)(lVar15 + 0x24),lVar15 + 0x30,lVar15 + 0x430,
                                    lVar15 + 0x230,lVar15 + 0x530);
      }
      else {
        uVar11 = thunk_FUN_012aac96();
        LOCK();
        plVar1 = (long *)(lVar10 + 0x13410);
        lVar12 = *plVar1;
        *plVar1 = *plVar1 + 1;
        UNLOCK();
        iVar14 = (int)lVar12;
        LOCK();
        plVar1 = (long *)(lVar10 + 0x13418);
        lVar2 = *plVar1;
        *plVar1 = *plVar1 + 1;
        UNLOCK();
        lVar12 = (long)(int)(iVar14 - (((uint)(lVar12 >> 0x3f) >> 0x1d) + iVar14 & 0xfffffff8)) *
                 0x20;
        plVar1 = (long *)(lVar10 + 0x13310 + lVar12);
        plVar1[3] = 0;
        plVar1[2] = 0;
        plVar1[1] = 0;
        *plVar1 = 0;
        *plVar1 = lVar2 + 1;
        *(undefined8 *)(lVar10 + 0x13318 + lVar12) = uVar11;
        lVar10 = *param_1;
        iVar16 = (int)*(undefined8 *)(lVar10 + 0x13410);
        iVar16 = iVar16 - (((uint)((long)*(undefined8 *)(lVar10 + 0x13410) >> 0x3f) >> 0x1d) +
                           iVar16 & 0xfffffff8);
        iVar14 = iVar16;
        do {
          lVar8 = (long)iVar14 * 0x20;
          lVar12 = *(long *)(lVar10 + 0x13320 + lVar8);
          if (lVar12 != 0) {
            lVar3 = *(long *)(lVar10 + 0x13310 + lVar8);
            if ((*(long *)(lVar10 + 0x13420) < lVar3) ||
               ((lVar3 < 1000 && (1000000 < *(long *)(lVar10 + 0x13420))))) {
              lVar4 = *(long *)(lVar10 + 0x13318 + lVar8);
              lVar9 = FUN_00068ea0();
              if (*(int *)(lVar10 + 0x13428) == 0) {
                *(undefined4 *)(lVar10 + 0x13428) = 1;
              }
              else {
                auVar17._8_8_ = 0;
                auVar17._0_8_ = lVar12 - lVar4;
                auVar17 = vpunpckldq_avx(auVar17,_DAT_0165fde0);
                auVar17 = vsubpd_avx(auVar17,_DAT_0165fdf0);
                if (DAT_0165fe38 < (auVar17._0_8_ + auVar17._8_8_) / (double)lVar9) {
                  *(undefined4 *)(lVar10 + 0x13428) = 0;
                  thunk_FUN_012aac96();
                }
              }
              *(undefined8 *)(lVar10 + 0x13430) = *(undefined8 *)(lVar10 + 0x13320 + lVar8);
              *(long *)(lVar10 + 0x13420) = lVar3;
            }
          }
          iVar14 = (iVar14 + 1) - (iVar14 + 1 + ((uint)(iVar14 + 1 >> 0x1f) >> 0x1d) & 0xfffffff8);
        } while (iVar14 != iVar16);
        thunk_FUN_012aba66(*(undefined4 *)(*param_1 + 0x80),*(undefined4 *)(lVar10 + 0x13428));
        iVar14 = thunk_FUN_012ac606(*(undefined4 *)(lVar15 + 0x24),lVar15 + 0x30,lVar15 + 0x430,
                                    lVar15 + 0x230,lVar15 + 0x530,*(undefined4 *)(*param_1 + 0x80),
                                    *(undefined4 *)(*param_1 + 0xb0),1,lVar2 + 1);
      }
      if ((iVar14 != 0) && (*(char *)(lVar15 + 0x28) != '\0')) {
        param_1[0xb] = lVar15;
        param_1[10] = (long)(param_1 + (ulong)*(uint *)(lVar15 + 0x20) * 0x1cc + 0xc);
        *(undefined4 *)(lVar15 + 0x24) = 0;
        uVar6 = FUN_007efc00();
        FUN_00f7d2f0(param_1[10],*(undefined8 *)(lVar15 + 0x30),uVar6,0,0);
        ((undefined8 *)param_1[10])[0x191] = *(undefined8 *)param_1[10];
        *(ulong *)(param_1[10] + 0xca0) = *(long *)(lVar15 + 0x30) + (ulong)(uVar6 & 0xfffffffc);
        lVar10 = param_1[10];
        uVar11 = *(undefined8 *)(lVar15 + 0x230);
        uVar7 = FUN_007efc00(&DAT_026e4840);
        FUN_00f7d2f0(lVar10 + 0x80,uVar11,uVar7,0,0);
        *(undefined8 *)(param_1[10] + 0xc98) = *(undefined8 *)(param_1[10] + 0x80);
        *(ulong *)(param_1[10] + 0xcb0) = (ulong)(uVar6 & 0xfffffffc) + *(long *)(lVar15 + 0x230);
        FUN_00f8ede0(param_1[10]);
        lVar10 = param_1[10];
        if (*(long *)(lVar10 + 0x40) != 0) {
          FUN_00f84db0(lVar10 + 0x40);
        }
        FUN_00f7e5e0(lVar10);
        *(undefined2 *)(lVar10 + 0xc84) = 0;
        *(undefined4 *)(lVar10 + 0xc80) = 0;
        FUN_00f80c90(param_1[10],4,0,DAT_026e4860,1,
                     *(undefined4 *)(DAT_026e4840 + (ulong)*(uint *)(lVar15 + 0x1c) * 8),0,0);
        FUN_00f81220(param_1[10]);
        FUN_007db810(param_1[0xb],param_1[10],4,0xffffffff,1);
        *(undefined8 *)param_1[10] = ((undefined8 *)param_1[10])[2];
        *(undefined8 *)(param_1[10] + 0x80) = *(undefined8 *)(param_1[10] + 0x90);
        thunk_FUN_012ac606(*(undefined4 *)(lVar15 + 0x24),lVar15 + 0x30,lVar15 + 0x430,
                           lVar15 + 0x230,lVar15 + 0x530,*(undefined4 *)(*param_1 + 0x80),
                           *(undefined4 *)(*param_1 + 0xb0),1,0);
        param_1[0xb] = 0;
        param_1[10] = 0;
      }
      lVar10 = *param_1;
      uVar6 = *(uint *)(lVar10 + 0x2cc);
    } while (0x80000000 < uVar6 - *(int *)(lVar10 + 0x2c8));
  }
  if (*(char *)(lVar10 + 0x2d8) != '\0') {
    FUN_000f2dc0(*(undefined4 *)(lVar10 + 0x2d4),0);
  }
  if (*DAT_01a1f100 != local_38) {
    uVar11 = thunk_FUN_012aa7f6();
    return uVar11;
  }
  return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),1);
}

