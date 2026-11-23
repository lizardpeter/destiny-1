
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_000cf100(void)

{
  int *piVar1;
  undefined4 uVar2;
  int iVar3;
  bool bVar4;
  bool bVar5;
  undefined2 uVar6;
  int iVar7;
  int iVar8;
  long lVar9;
  undefined8 uVar10;
  long lVar11;
  long lVar12;
  long lVar13;
  ushort uVar14;
  uint uVar15;
  ulong uVar16;
  undefined *puVar17;
  ushort uVar18;
  ushort uVar19;
  short sVar20;
  short local_5a;
  undefined1 local_58 [16];
  undefined4 local_48 [4];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  if (DAT_0257a038 == 0) {
    lVar9 = FUN_000f2280(&DAT_0256c880);
    lVar11 = 0;
    if (lVar9 == 0) {
      lVar12 = 0;
    }
    else {
      do {
        lVar12 = lVar9;
        lVar9 = FUN_00058050(lVar12);
        FUN_000f2150(lVar12,lVar11);
        lVar11 = lVar12;
      } while (lVar9 != 0);
    }
    DAT_0257a038 = lVar12;
    if (lVar12 == 0) goto LAB_000cfb1e;
  }
  bVar5 = false;
  do {
    lVar9 = DAT_0257a038;
    if (bVar5) break;
    bVar4 = bVar5;
    switch(*(undefined1 *)(DAT_0257a038 + 8)) {
    case 1:
      FUN_000e0660(*(undefined4 *)(DAT_0257a038 + 0x10));
      break;
    case 2:
      FUN_000e06d0(*(undefined4 *)(DAT_0257a038 + 0x10));
      break;
    case 3:
      local_5a = FUN_000e0750(*(undefined4 *)(DAT_0257a038 + 0x10));
      if (local_5a != -1) {
        FUN_000e0e60(&local_5a);
      }
      break;
    case 4:
      uVar2 = *(undefined4 *)(DAT_0257a038 + 0x10);
      uVar18 = FUN_00077100(&DAT_0256c8e0,1,&DAT_0257a030);
      lVar9 = DAT_0256c8e0;
      lVar11 = (ulong)uVar18 * DAT_0256c8f0;
      *(undefined4 *)((long)&DAT_0256c8e0 + lVar11 + DAT_0256c8e0) = uVar2;
      *(undefined1 *)((long)&DAT_0256c8e0 + lVar11 + 4 + lVar9) = 1;
      goto LAB_000cf634;
    case 5:
      if (DAT_0257a030 == 0xffff) {
        uVar18 = 0xffff;
      }
      else {
        uVar18 = DAT_0257a030;
        do {
          if (*(int *)((long)&DAT_0256c8e0 + (ulong)uVar18 * DAT_0256c8f0 + DAT_0256c8e0) ==
              *(int *)(DAT_0257a038 + 0x10)) goto LAB_000cf5d3;
        } while ((uVar18 != 0xffff) &&
                (uVar18 = *(ushort *)((long)&DAT_0256c8e8 + (ulong)uVar18 * 4 + DAT_0256c8e8),
                uVar18 != 0xffff));
        uVar18 = 0xffff;
      }
LAB_000cf5d3:
      *(undefined1 *)((ulong)uVar18 * DAT_0256c8f0 + DAT_0256c8e0 + 0x256c8e4) = 1;
      break;
    case 6:
      uVar19 = 0xffff;
      uVar18 = uVar19;
      if (DAT_0257a030 != 0xffff) {
        uVar14 = DAT_0257a030;
        do {
          uVar18 = uVar14;
          if ((*(int *)((long)&DAT_0256c8e0 + (ulong)uVar14 * DAT_0256c8f0 + DAT_0256c8e0) ==
               *(int *)(DAT_0257a038 + 0x10)) || (uVar18 = uVar19, uVar14 == 0xffff)) break;
          uVar14 = *(ushort *)((long)&DAT_0256c8e8 + (ulong)uVar14 * 4 + DAT_0256c8e8);
        } while (uVar14 != 0xffff);
      }
      FUN_00077290(&DAT_0256c8e0,&DAT_0257a030,uVar18);
LAB_000cf634:
      FUN_000e0ee0(1,1);
      break;
    case 7:
      FUN_000e0f60();
      for (uVar18 = DAT_0257a030; uVar18 != 0xffff;
          uVar18 = *(ushort *)((long)&DAT_0256c8e8 + (ulong)uVar18 * 4 + DAT_0256c8e8)) {
        *(undefined1 *)(DAT_0256c8f0 * (ulong)uVar18 + DAT_0256c8e0 + 0x256c8e4) = 0;
      }
      break;
    case 8:
      if ((ulong)DAT_025545f8._6_2_ != 0xffff) {
        uVar15 = *(uint *)((long)&DAT_02554610 +
                          (ulong)DAT_025545f8._6_2_ * DAT_02554620 + DAT_02554610);
        bVar5 = true;
        if ((0x19 < uVar15) || ((0x2810000U >> (uVar15 & 0x1f) & 1) == 0)) goto LAB_000cf8e7;
      }
      if ((int)DAT_025545f8 == 1) {
        FUN_000d4e10(DAT_025545f8._6_2_,0xffffffb7);
        FUN_000ccb60(DAT_025545f8._6_2_);
      }
      FUN_000af380();
      FUN_000dff80();
      DAT_025545f8._4_2_ = *(short *)(DAT_0257a038 + 0x18);
      DAT_025545f8._0_4_ = 2;
      _DAT_025545d8 = 0;
      DAT_025545e8 = 0xffffffffffffffff;
      FUN_000cff90(*(undefined2 *)(DAT_0257a038 + 0x18));
      break;
    case 9:
      bVar4 = true;
      if (DAT_025545f8._4_2_ == -1) {
        bVar4 = bVar5;
      }
      break;
    case 10:
      bVar5 = true;
      if (DAT_025545f8._4_2_ == -1) {
        FUN_000e2080(&DAT_02587a58,&DAT_025546d4 + (DAT_025546d0 + -1));
        DAT_025546d0 = DAT_025546d0 + -1;
        break;
      }
      goto LAB_000cf8e7;
    case 0xb:
      bVar4 = true;
      if (DAT_025545f8._4_2_ == -1) {
        bVar4 = bVar5;
      }
      break;
    case 0xc:
      lVar9 = (long)DAT_0254c540;
      DAT_0254c540 = DAT_0254c540 + 1;
      (&DAT_0254c548)[lVar9 * 6] = *(undefined4 *)(DAT_0257a038 + 0x10);
      (&DAT_0254c55c)[lVar9 * 6] = 0;
      (&DAT_0254c558)[lVar9 * 6] = 0xffffffff;
      uVar10 = FUN_000e3d70();
      (&DAT_0254c550)[lVar9 * 3] = uVar10;
      break;
    case 0xd:
      uVar2 = *(undefined4 *)(DAT_0257a038 + 0x14);
      lVar9 = (long)DAT_0254d148;
      DAT_0254d148 = DAT_0254d148 + 1;
      *(undefined4 *)(&DAT_0254d14c + lVar9 * 0xc) = *(undefined4 *)(DAT_0257a038 + 0x10);
      (&DAT_0254d150)[lVar9 * 3] = uVar2;
      (&DAT_0254d154)[lVar9 * 3] = 0;
      break;
    case 0xf:
      lVar11 = *(long *)(DAT_0257a038 + 0x10);
      local_48[0] = *(undefined4 *)(lVar11 + 0x108);
      iVar7 = FUN_000d6300(lVar11,local_48,(int)*(short *)(lVar11 + 0x10c),
                           *(undefined8 *)(lVar11 + 0x100),0);
      if (iVar7 != 1) {
        DAT_0254febc = iVar7;
      }
      FUN_000b4d40(*(undefined8 *)(lVar9 + 0x10));
      goto LAB_000cf4d4;
    case 0x10:
      iVar7 = FUN_000d7250((int)*(short *)(DAT_0257a038 + 0x10));
      if (iVar7 != 1) {
        DAT_0254febc = iVar7;
      }
LAB_000cf4d4:
      LOCK();
      DAT_0254feb8 = DAT_0254feb8 + -1;
      UNLOCK();
      break;
    case 0x11:
      bVar5 = true;
      if (DAT_025545f8._4_2_ == -1) {
        if ((char)_DAT_0254fed8 == '\0') {
          if (DAT_0254fed0 != -1) {
            iVar7 = FUN_000d7980(DAT_0254fed0);
            if (iVar7 < 1) {
              DAT_0254fed4 = 0;
              DAT_02554530 = DAT_02554530 + 1;
              DAT_02554534 = DAT_02554534 + 1;
              DAT_0254fed0 = FUN_000d8910(DAT_0254fed0);
            }
            else if (iVar7 == 1) {
              FUN_00082c40(local_58);
              lVar9 = FUN_000d6fa0(DAT_0254fed0);
              uVar6 = FUN_000d6f90((int)*(short *)(lVar9 + 4));
              lVar11 = FUN_000d6fa0(uVar6);
              iVar7 = 1;
              while (((9 < DAT_02546128 - DAT_02546130 && (iVar8 = FUN_00083a60(), 9 < iVar8)) &&
                     (iVar7 == 1))) {
                lVar12 = FUN_000d88e0(lVar9,DAT_0254fed4);
                if (*(short *)(lVar12 + 8) == *(short *)(lVar9 + 0x20)) {
                  uVar16 = (long)(int)(DAT_0254612c + DAT_02546130) % (long)DAT_02546128;
                  DAT_02546130 = DAT_02546130 + 1;
                  lVar13 = (long)(int)uVar16;
                  *(undefined4 *)(&DAT_02546138 + lVar13 * 0x28) = 0xffffffff;
                  piVar1 = &DAT_02546158 + lVar13 * 10;
                  *(undefined8 *)(&DAT_02546150 + lVar13 * 0x28) = 0;
                  *(undefined8 *)(&DAT_02546148 + lVar13 * 0x28) = 0;
                  *(undefined8 *)(&DAT_02546140 + lVar13 * 0x28) = 0;
                  *(undefined **)(&DAT_02546140 + lVar13 * 0x28) = &DAT_0254fec0;
                  *(undefined8 *)(&DAT_02546148 + lVar13 * 0x28) = 0x10;
                  *(undefined8 *)(&DAT_02546150 + lVar13 * 0x28) = 0;
                  *(uint *)(&DAT_02546138 + lVar13 * 0x28) =
                       (uint)*(ushort *)(lVar12 + 8) * 0x10000 + (int)*(short *)(lVar9 + 4) |
                       0xc0000000;
                  do {
                    iVar3 = *piVar1;
                    LOCK();
                    iVar8 = *piVar1;
                    if (iVar3 == iVar8) {
                      *piVar1 = 1;
                      iVar8 = iVar3;
                    }
                    UNLOCK();
                  } while (iVar3 != iVar8);
                  LOCK();
                  DAT_0254c538 = DAT_0254c538 + 1;
                  UNLOCK();
                  uVar6 = FUN_00083e30(*(undefined4 *)(lVar9 + 0x270),&DAT_0254fec0,lVar12,0,0x10,1,
                                       FUN_000d3470,uVar16 & 0xffffffff);
                  *(undefined2 *)(&DAT_0254613c + lVar13 * 0x28) = uVar6;
                }
                DAT_0254fed4 = DAT_0254fed4 + 1;
                if (DAT_0254fed4 == *(int *)(lVar11 + 0xd0)) {
                  DAT_0254fed4 = 0;
                  DAT_02554530 = DAT_02554530 + 1;
                  DAT_0254fed0 = FUN_000d8910(DAT_0254fed0);
                  iVar7 = 2;
                  if (DAT_0254fed0 != -1) {
                    lVar9 = FUN_000d6fa0(DAT_0254fed0);
                    iVar7 = 2;
                    if (*(short *)(lVar9 + 4) != *(short *)(lVar11 + 4)) {
                      FUN_000d83c0();
                    }
                  }
                }
              }
              FUN_00082c70(local_58);
            }
          }
        }
        else {
          if (_DAT_0254fed8 < 0x100) {
            _DAT_0254fed8 = CONCAT11(1,(char)_DAT_0254fed8);
            FUN_00082c40(local_48);
            uVar15 = 0xffffffff;
            if (DAT_02546130 != 0) {
              uVar15 = DAT_0254612c;
            }
            for (; uVar15 != 0xffffffff; uVar15 = (int)(uVar15 + 1) % DAT_02546128) {
              if ((&DAT_02546158)[(long)(int)uVar15 * 10] == 1) {
                FUN_000842f0(*(undefined2 *)(&DAT_0254613c + (long)(int)uVar15 * 0x28));
              }
              if (((uVar15 == 0xffffffff) ||
                  (iVar7 = (int)((uVar15 - DAT_0254612c) + DAT_02546128) % DAT_02546128, iVar7 < 0))
                 || (DAT_02546130 + -1 <= iVar7)) break;
            }
            FUN_00082c70(local_48);
          }
          DAT_0254fed0 = -1;
        }
        uVar16 = 0xffffffff;
        if (DAT_02546130 != 0) {
          uVar16 = (ulong)DAT_0254612c;
        }
        while ((int)uVar16 != -1) {
          lVar9 = (long)(int)uVar16;
          uVar15 = (&DAT_02546158)[lVar9 * 10];
          uVar18 = (ushort)((uint)*(undefined4 *)(&DAT_02546138 + lVar9 * 0x28) >> 0x10) & 0x3fff;
          lVar11 = (long)DAT_0254fedc;
          sVar20 = (short)*(undefined4 *)(&DAT_02546138 + lVar9 * 0x28);
          if (((lVar11 < 1) ||
              (lVar12 = (long)(DAT_0254fedc + -1),
              *(short *)(&DAT_0254fee0 + lVar12 * 0xc) != sVar20)) ||
             ((puVar17 = &DAT_0254fee0 + lVar12 * 0xc, puVar17 == (undefined *)0x0 ||
              (*(ushort *)(&DAT_0254fee2 + lVar12 * 0xc) != uVar18)))) {
            DAT_0254fedc = DAT_0254fedc + 1;
            *(undefined4 *)(&DAT_0254fee8 + lVar11 * 0xc) = 0;
            *(undefined8 *)(&DAT_0254fee0 + lVar11 * 0xc) = 0;
            *(short *)(&DAT_0254fee0 + lVar11 * 0xc) = sVar20;
            *(ushort *)(&DAT_0254fee2 + lVar11 * 0xc) = uVar18;
            *(undefined4 *)(&DAT_0254fee8 + lVar11 * 0xc) = 0xffffffff;
            puVar17 = &DAT_0254fee0 + lVar11 * 0xc;
          }
          if (uVar15 < 0xd) {
            if (uVar15 == 2) {
LAB_000cf86b:
              *(short *)(puVar17 + 6) = *(short *)(puVar17 + 6) + 1;
            }
            else if (uVar15 != 3) {
              if (uVar15 != 1) goto LAB_000cf871;
              break;
            }
          }
          else {
            if (uVar15 == 0x13) break;
            if (uVar15 == 0xd) goto LAB_000cf86b;
LAB_000cf871:
            *(short *)(puVar17 + 6) = *(short *)(puVar17 + 6) + 1;
            *(short *)(puVar17 + 4) = *(short *)(puVar17 + 4) + 1;
            DAT_02554538 = DAT_02554538 + 1;
            *(uint *)(puVar17 + 8) = uVar15;
          }
          *(undefined8 *)(&DAT_02546148 + lVar9 * 0x28) = 0;
          *(undefined4 *)(&DAT_02546138 + lVar9 * 0x28) = 0xffffffff;
          *(undefined8 *)(&DAT_02546140 + lVar9 * 0x28) = 0;
          if (DAT_02546130 == 0) break;
          uVar16 = (long)(int)(DAT_0254612c + 1) % (long)DAT_02546128;
          DAT_0254612c = (uint)uVar16;
          DAT_02546130 = DAT_02546130 + -1;
          uVar16 = uVar16 & 0xffffffff;
          if (DAT_02546130 == 0) {
            uVar16 = 0xffffffff;
          }
        }
        lVar9 = DAT_0257a038;
        if (DAT_0254fed0 == -1) {
          bVar5 = true;
          if (DAT_02546130 == 0) break;
        }
        else {
          bVar5 = true;
        }
      }
      goto LAB_000cf8e7;
    }
    lVar11 = DAT_0257a038;
    lVar9 = DAT_0257a038;
    bVar5 = bVar4;
    if (!bVar4) {
      lVar9 = FUN_00058050(DAT_0257a038);
      FUN_000f2160(&DAT_0256c890,lVar11);
      if (lVar9 == 0) {
        DAT_0257a038 = lVar9;
        lVar11 = FUN_000f2280(&DAT_0256c880);
        lVar9 = 0;
        while (lVar12 = lVar11, lVar12 != 0) {
          lVar11 = FUN_00058050(lVar12);
          FUN_000f2150(lVar12,lVar9);
          lVar9 = lVar12;
        }
      }
    }
LAB_000cf8e7:
    DAT_0257a038 = lVar9;
  } while (DAT_0257a038 != 0);
LAB_000cfb1e:
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

