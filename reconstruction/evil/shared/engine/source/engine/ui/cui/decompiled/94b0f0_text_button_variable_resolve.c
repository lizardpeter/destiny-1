
undefined8 FUN_0094b0f0(uint *param_1,uint *param_2)

{
  byte bVar1;
  char cVar2;
  undefined1 uVar3;
  uint uVar4;
  uint uVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  undefined8 uVar8;
  undefined4 *puVar9;
  long lVar10;
  ulong uVar11;
  uint *puVar12;
  long lVar13;
  uint *puVar14;
  long lVar15;
  ulong uVar16;
  int iVar17;
  int iVar18;
  undefined1 local_51;
  uint local_50 [2];
  uint local_48 [2];
  uint local_40 [2];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  uVar5 = *param_1;
  uVar8 = FUN_001de430();
  cVar2 = FUN_001de350(uVar8);
  iVar17 = -1;
  local_51 = 0;
  uVar4 = *param_1;
  if (uVar4 < 0xf781d815) {
    if (0xf5b6e399 < uVar4) {
      if (uVar4 != 0xf5b6e39a) goto LAB_0094bd18;
      lVar15 = 0xe;
      goto LAB_0094babc;
    }
    if (uVar4 < 0x4174884) {
      if (uVar4 != 0x2c78cf2) goto LAB_0094bd18;
      lVar15 = 0x1a;
      goto LAB_0094babc;
    }
    if (uVar4 < 0x8943374) {
      if (uVar4 != 0x4174884) goto LAB_0094bd18;
      lVar15 = 1;
      goto LAB_0094babc;
    }
    if (uVar4 < 0xbca0dcf) {
      if (uVar4 != 0x8943374) goto LAB_0094bd18;
      lVar15 = 0x18;
      goto LAB_0094babc;
    }
    if (uVar4 < 0xedb7051) {
      if (uVar4 != 0xbca0dcf) goto LAB_0094bd18;
      lVar15 = 8;
      goto LAB_0094babc;
    }
    if (0x149b8886 < uVar4) {
      if (uVar4 < 0x17339f15) {
        if (uVar4 != 0x149b8887) goto LAB_0094bd18;
        uVar6 = 10;
        goto LAB_0094bc43;
      }
      if (uVar4 < 0x191c9d9c) {
        if (uVar4 != 0x17339f15) goto LAB_0094bd18;
        lVar15 = 0x15;
        goto LAB_0094babc;
      }
      if (uVar4 < 0x1bcc3ef3) {
        if (uVar4 != 0x191c9d9c) goto LAB_0094bd18;
        lVar15 = 0x10;
        goto LAB_0094babc;
      }
      if (uVar4 < 0x23705889) {
        if (uVar4 != 0x1bcc3ef3) goto LAB_0094bd18;
        uVar6 = 0x14;
        goto LAB_0094bc43;
      }
      if (uVar4 < 0x26697bd6) {
        if (uVar4 != 0x23705889) goto LAB_0094bd18;
        uVar6 = 9;
        goto LAB_0094bc43;
      }
      if (uVar4 < 0x2e876827) {
        if (uVar4 != 0x26697bd6) goto LAB_0094bd18;
        lVar15 = 10;
LAB_0094b391:
        uVar5 = FUN_00587880();
        iVar17 = 0;
        if ((uVar5 < 4) && (lVar10 = FUN_009496e0(uVar5), iVar17 = 0, lVar10 != 0)) {
          iVar17 = (int)*(char *)(lVar10 + 0x11);
        }
        uVar6 = FUN_00587880();
        uVar3 = FUN_00528790(uVar6);
        uVar8 = FUN_00748fe0(iVar17,*(undefined4 *)(&DAT_015dc5b0 + lVar15 * 4),uVar3);
        iVar17 = FUN_00745650(uVar8,lVar15);
        if (iVar17 == -1) {
          uVar6 = FUN_00587880();
          cVar2 = FUN_00528790(uVar6);
          puVar12 = &DAT_027448e4;
          puVar14 = &DAT_027448e0;
LAB_0094ba84:
          if (cVar2 != '\0') {
            puVar14 = puVar12;
          }
          local_48[0] = *puVar14;
          goto switchD_0094bb36_default;
        }
        goto LAB_0094bb17;
      }
      if (uVar4 < 0x314a1db1) {
        lVar15 = 0;
        if (uVar4 != 0x2e876827) goto LAB_0094bd18;
        goto LAB_0094babc;
      }
      if (uVar4 < 0x4185f617) {
        if (uVar4 != 0x314a1db1) goto LAB_0094bd18;
        lVar15 = 0x12;
        goto LAB_0094babc;
      }
      if (uVar4 < 0x44d1f0fe) {
        if (uVar4 != 0x4185f617) goto LAB_0094bd18;
        uVar6 = 0xc;
        goto LAB_0094bc84;
      }
      if (uVar4 < 0x49b9baff) {
        if (uVar4 != 0x44d1f0fe) goto LAB_0094bd18;
        lVar15 = 0x1c;
        iVar17 = 2;
        goto LAB_0094babc;
      }
      if (uVar4 < 0x4d020709) {
        if (uVar4 != 0x49b9baff) goto LAB_0094bd18;
        uVar6 = 0xd;
        goto LAB_0094bc43;
      }
      if (uVar4 < 0x50863045) {
        if (uVar4 != 0x4d020709) goto LAB_0094bd18;
        lVar15 = 0x19;
        goto LAB_0094babc;
      }
      if (uVar4 < 0x58e6ac05) {
        lVar15 = 2;
        if (uVar4 != 0x50863045) goto LAB_0094bd18;
        goto LAB_0094b391;
      }
      if (uVar4 < 0x5d5c8072) {
        if (uVar4 != 0x58e6ac05) goto LAB_0094bd18;
        uVar4 = FUN_00587880();
        local_48[0] = DAT_0274483c;
        if ((((uVar4 < 4) && (lVar15 = FUN_009496e0(uVar4), local_48[0] = DAT_0274483c, lVar15 != 0)
             ) && (bVar1 = *(byte *)(lVar15 + 0x11), 4 < bVar1)) &&
           ((bVar1 != 6 && (local_48[0] = uVar5, bVar1 == 5)))) {
          local_48[0] = DAT_0274485c;
        }
        goto switchD_0094bb36_default;
      }
      if (uVar4 < 0x6bf3bb5c) {
        if (uVar4 != 0x5d5c8072) goto LAB_0094bd18;
LAB_0094b9c8:
        lVar15 = 7;
        goto LAB_0094babc;
      }
      if (uVar4 < 0x6febe322) {
        if (uVar4 != 0x6bf3bb5c) goto LAB_0094bd18;
        lVar15 = 0x13;
        goto LAB_0094babc;
      }
      if (uVar4 < 0x747868d5) {
        if (uVar4 != 0x6febe322) goto LAB_0094bd18;
        lVar15 = 6;
        goto LAB_0094babc;
      }
      if (uVar4 < 0x768ed8ce) {
        if (uVar4 != 0x747868d5) goto LAB_0094bd18;
        lVar15 = 0x16;
        goto LAB_0094babc;
      }
      if (0xee92d2f5 < uVar4) {
        if (uVar4 != 0xee92d2f6) goto LAB_0094bd18;
        goto switchD_0094bb36_caseD_10;
      }
      if (0xedaadc9a < uVar4) {
        if (uVar4 != 0xedaadc9b) goto LAB_0094bd18;
        lVar15 = 0x14;
        goto LAB_0094babc;
      }
      if (0xebaaf853 < uVar4) {
        if (uVar4 != 0xebaaf854) goto LAB_0094bd18;
        uVar5 = FUN_00587880();
        uVar16 = 0;
        if ((((uVar5 < 4) && (lVar15 = FUN_009496e0(uVar5), lVar15 != 0)) &&
            (uVar16 = (ulong)*(char *)(lVar15 + 0x12), 3 < uVar16)) ||
           ((local_48[0] = DAT_027448c8, (&DAT_0166d0d0)[uVar16] != 1 &&
            (local_48[0] = 0x811c9dc5, (&DAT_0166d0d0)[uVar16] == 0)))) {
          local_48[0] = DAT_027448d8;
        }
        goto switchD_0094bb36_default;
      }
      if (0xeabfe98f < uVar4) {
        if (uVar4 != 0xeabfe990) goto LAB_0094bd18;
        lVar15 = 0x15;
        iVar17 = 2;
        goto LAB_0094babc;
      }
      if (0xe65dd48d < uVar4) {
        if (uVar4 != 0xe65dd48e) goto LAB_0094bd18;
        uVar6 = 3;
        goto LAB_0094bc43;
      }
      if (0xd5c2f6f5 < uVar4) {
        if (uVar4 != 0xd5c2f6f6) goto LAB_0094bd18;
        uVar6 = 0xb;
        goto LAB_0094bc43;
      }
      if (0xd17309a3 < uVar4) {
        if (uVar4 != 0xd17309a4) goto LAB_0094bd18;
        lVar15 = 0x15;
        iVar17 = 3;
        goto LAB_0094babc;
      }
      if (uVar4 < 0x774c42e1) {
        if (uVar4 != 0x768ed8ce) goto LAB_0094bd18;
        uVar6 = 0x12;
        goto LAB_0094bc43;
      }
      if (uVar4 < 0x77d5b3e7) {
        if (uVar4 != 0x774c42e1) goto LAB_0094bd18;
        uVar5 = FUN_00587880();
        uVar16 = 0;
        if ((uVar5 < 4) && (lVar15 = FUN_009496e0(uVar5), lVar15 != 0)) {
          uVar16 = (ulong)*(char *)(lVar15 + 0x12);
          uVar6 = 0x11;
          if (uVar16 < 4) goto LAB_0094b65e;
        }
        else {
LAB_0094b65e:
          puVar9 = (undefined4 *)&DAT_0166d0f0;
LAB_0094b877:
          uVar6 = puVar9[uVar16];
        }
LAB_0094b87a:
        FUN_0094c240(local_48,uVar6);
        goto switchD_0094bb36_default;
      }
      if (uVar4 < 0x82f021d8) {
        if (uVar4 != 0x77d5b3e7) goto LAB_0094bd18;
        uVar6 = 2;
        goto LAB_0094bc43;
      }
      if (uVar4 < 0x8feb4850) {
        if (uVar4 != 0x82f021d8) goto LAB_0094bd18;
        iVar17 = 3;
        lVar15 = 3;
        goto LAB_0094babc;
      }
      if (uVar4 < 0x92f2735c) {
        if (uVar4 != 0x8feb4850) goto LAB_0094bd18;
        lVar15 = 5;
        goto LAB_0094babc;
      }
      if (uVar4 < 0x94ba9098) {
        if (uVar4 != 0x92f2735c) goto LAB_0094bd18;
        uVar6 = 0xf;
        goto LAB_0094bc43;
      }
      if (uVar4 < 0x9a881c86) {
        uVar6 = 0xb;
        if (uVar4 != 0x94ba9098) goto LAB_0094bd18;
        goto LAB_0094bc84;
      }
      if (uVar4 < 0x9b69e2cf) {
        if (uVar4 != 0x9a881c86) goto LAB_0094bd18;
        uVar6 = 0x13;
        goto LAB_0094bc43;
      }
      if (uVar4 < 0x9cc71cf0) {
        if (uVar4 != 0x9b69e2cf) goto LAB_0094bd18;
        lVar15 = 0xf;
        goto LAB_0094babc;
      }
      if (0xcf0d9b3f < uVar4) {
        if (uVar4 != 0xcf0d9b40) goto LAB_0094bd18;
        uVar5 = FUN_00587880();
        uVar16 = 0;
        if ((uVar5 < 4) && (lVar15 = FUN_009496e0(uVar5), lVar15 != 0)) {
          uVar16 = (ulong)*(char *)(lVar15 + 0x12);
          uVar6 = 9;
          if (3 < uVar16) goto LAB_0094b87a;
        }
        puVar9 = &DAT_0166d100;
        goto LAB_0094b877;
      }
      if (0xced69a4d < uVar4) {
        if (uVar4 != 0xced69a4e) goto LAB_0094bd18;
        puVar14 = &DAT_02744824;
        if (cVar2 != '\0') {
          puVar14 = (uint *)PTR_DAT_01a1f5e0;
        }
        local_48[0] = *puVar14;
        goto switchD_0094bb36_default;
      }
      if (0xce4ea330 < uVar4) {
        if (uVar4 != 0xce4ea331) goto LAB_0094bd18;
        uVar6 = 0xe;
        goto LAB_0094bc43;
      }
      if (0xcdb01873 < uVar4) {
        if (uVar4 != 0xcdb01874) goto LAB_0094bd18;
        uVar6 = 5;
        goto LAB_0094bc43;
      }
      if (0xcc517dbd < uVar4) {
        if (uVar4 != 0xcc517dbe) goto LAB_0094bd18;
        puVar14 = &DAT_02744828;
        if (cVar2 != '\0') {
          puVar14 = (uint *)PTR_DAT_01a1f5e8;
        }
        local_48[0] = *puVar14;
        goto switchD_0094bb36_default;
      }
      if (0xc75e923e < uVar4) {
        if (uVar4 != 0xc75e923f) goto LAB_0094bd18;
        uVar6 = 0x11;
        goto LAB_0094bc43;
      }
      if (0xc5578819 < uVar4) {
        if (uVar4 != 0xc557881a) goto LAB_0094bd18;
        uVar6 = 0;
        goto LAB_0094bc43;
      }
      if (0xc4521a03 < uVar4) {
        uVar6 = 0xc;
        if (uVar4 != 0xc4521a04) goto LAB_0094bd18;
        goto LAB_0094bc43;
      }
      if (0xc2be5d1e < uVar4) {
        if (uVar4 != 0xc2be5d1f) goto LAB_0094bd18;
        uVar5 = FUN_00587880();
        uVar16 = 0;
        if ((((3 < uVar5) || (lVar15 = FUN_009496e0(uVar5), lVar15 == 0)) ||
            (uVar16 = (ulong)*(char *)(lVar15 + 0x12), local_48[0] = DAT_027448c8, uVar16 < 4)) &&
           ((local_48[0] = DAT_027448c8, (&DAT_0166d0e0)[uVar16] != 1 &&
            (local_48[0] = 0x811c9dc5, (&DAT_0166d0e0)[uVar16] == 0)))) {
          local_48[0] = DAT_027448d8;
        }
        goto switchD_0094bb36_default;
      }
      if (uVar4 < 0xbe22697b) {
        if (uVar4 < 0xb96feffc) {
          if (0xaf17bf28 < uVar4) {
            if (uVar4 != 0xaf17bf29) goto LAB_0094bd18;
            goto LAB_0094b9c8;
          }
          if (uVar4 < 0xac84289d) {
            if (uVar4 < 0xa5e39c42) {
              if (0xa127b022 < uVar4) {
                if (uVar4 != 0xa127b023) goto LAB_0094bd18;
                uVar6 = 4;
                goto LAB_0094bc43;
              }
              if (0xa0ca899b < uVar4) {
                if (uVar4 != 0xa0ca899c) goto LAB_0094bd18;
                uVar5 = FUN_00587880();
                iVar17 = 0;
                if ((uVar5 < 4) && (lVar15 = FUN_009496e0(uVar5), iVar17 = 0, lVar15 != 0)) {
                  iVar17 = (int)*(char *)(lVar15 + 0x11);
                }
                uVar6 = FUN_00587880();
                uVar3 = FUN_00528790(uVar6);
                uVar8 = FUN_00748fe0(iVar17,0,uVar3);
                iVar17 = FUN_00745650(uVar8,0x1b);
                if (iVar17 == -1) {
                  uVar6 = FUN_00587880();
                  cVar2 = FUN_00528790(uVar6);
                  puVar12 = &DAT_027448e0;
                  puVar14 = &DAT_027448e4;
                  goto LAB_0094ba84;
                }
                goto LAB_0094bb17;
              }
              if (uVar4 < 0x9f6c517a) {
                if (uVar4 < 0x9f1b558d) {
                  if (uVar4 == 0x9cc71cf0) {
                    uVar6 = 0x10;
                  }
                  else {
                    if (uVar4 == 0x9cd0ef5e) {
                      lVar15 = 4;
                      goto LAB_0094babc;
                    }
                    if (uVar4 != 0x9db8ebbe) goto LAB_0094bd18;
                    uVar6 = 8;
                  }
                  goto LAB_0094bc43;
                }
                if (uVar4 != 0x9f1b558d) goto LAB_0094bd18;
                lVar15 = 3;
              }
              else {
                if (uVar4 != 0x9f6c517a) goto LAB_0094bd18;
                lVar15 = 0x1d;
                iVar17 = 3;
              }
            }
            else {
              if (uVar4 != 0xa5e39c42) goto LAB_0094bd18;
              lVar15 = 7;
            }
          }
          else {
            if (uVar4 != 0xac84289d) goto LAB_0094bd18;
            lVar15 = 0xd;
          }
        }
        else {
          if (uVar4 != 0xb96feffc) goto LAB_0094bd18;
          lVar15 = 0x16;
          iVar17 = 3;
        }
        goto LAB_0094babc;
      }
      if (uVar4 != 0xbe22697b) goto LAB_0094bd18;
      goto switchD_0094bb36_caseD_6;
    }
    if (uVar4 != 0xedb7051) goto LAB_0094bd18;
    uVar6 = 1;
LAB_0094bc43:
    uVar5 = FUN_00587880();
    iVar17 = 0;
    if ((uVar5 < 4) && (lVar15 = FUN_009496e0(uVar5), iVar17 = 0, lVar15 != 0)) {
      iVar17 = (int)*(char *)(lVar15 + 0x11);
    }
    uVar7 = FUN_00587880();
    uVar3 = FUN_00528790(uVar7);
    uVar8 = FUN_00748fe0(iVar17,0,uVar3);
    uVar6 = FUN_00745720(uVar8,uVar6);
LAB_0094bc84:
    FUN_0094c240(local_40,uVar6);
    local_48[0] = local_40[0];
  }
  else {
    if (uVar4 != 0xf781d815) goto LAB_0094bd18;
    lVar15 = 0x17;
LAB_0094babc:
    uVar5 = FUN_00587880();
    iVar18 = 0;
    if ((uVar5 < 4) && (lVar10 = FUN_009496e0(uVar5), iVar18 = 0, lVar10 != 0)) {
      iVar18 = (int)*(char *)(lVar10 + 0x11);
    }
    if ((iVar17 == -1) && (iVar17 = 0, (uint)lVar15 < 0x1b)) {
      iVar17 = *(int *)(&DAT_015dc5b0 + lVar15 * 4);
    }
    uVar6 = FUN_00587880();
    uVar3 = FUN_00528790(uVar6);
    uVar8 = FUN_00748fe0(iVar18,iVar17,uVar3);
    iVar17 = FUN_00745650(uVar8,lVar15);
LAB_0094bb17:
    local_48[0] = 0x811c9dc5;
    switch(iVar17) {
    case 0:
      local_48[0] = DAT_027448d0;
      break;
    case 1:
      local_48[0] = DAT_027448c0;
      break;
    case 2:
      local_48[0] = DAT_02744890;
      break;
    case 3:
      local_48[0] = DAT_02744894;
      break;
    case 4:
      local_48[0] = DAT_02744898;
      break;
    case 5:
      local_48[0] = DAT_0274489c;
      break;
    case 6:
switchD_0094bb36_caseD_6:
      local_48[0] = DAT_027448a0;
      break;
    case 7:
      local_48[0] = DAT_027448a4;
      break;
    case 8:
      local_48[0] = DAT_027448dc;
      break;
    case 9:
      local_48[0] = DAT_027448cc;
      break;
    case 10:
      local_48[0] = DAT_02744880;
      break;
    case 0xb:
      local_48[0] = DAT_02744884;
      break;
    case 0xc:
      local_48[0] = DAT_0274488c;
      break;
    case 0xd:
      local_48[0] = DAT_02744888;
      break;
    case 0xe:
      local_48[0] = DAT_027448d4;
      break;
    case 0xf:
      local_48[0] = DAT_027448c4;
      break;
    case 0x10:
switchD_0094bb36_caseD_10:
      local_48[0] = DAT_027448ac;
      break;
    case 0x11:
      local_48[0] = DAT_027448b0;
      break;
    case 0x12:
      local_48[0] = DAT_027448b4;
      break;
    case 0x13:
      local_48[0] = DAT_027448b8;
      break;
    case 0x14:
      local_48[0] = DAT_027448bc;
    }
  }
switchD_0094bb36_default:
  lVar15 = FUN_00ac5e40();
  if ((lVar15 != 0) && (uVar5 = *(uint *)(lVar15 + 8), uVar5 != 0xffffffff)) {
    lVar13 = (ulong)(((uint)((int)uVar5 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar5 >> 0xd) * 0x40;
    lVar15 = *DAT_01a238a0;
    lVar10 = *(long *)(lVar15 + 0x10 + lVar13);
    iVar17 = *(int *)(lVar15 + 0x34 + lVar13);
    uVar11 = (ulong)((uVar5 & 0x1fff) * *(int *)(lVar15 + 0x30 + lVar13));
    uVar16 = *(ulong *)(lVar10 + 8 + uVar11);
    local_50[0] = local_48[0];
    uVar6 = FUN_00752a40();
    lVar15 = FUN_008d5220((lVar10 + uVar11) - ((long)iVar17 & uVar16),local_50,uVar6);
    if (lVar15 != 0) {
      *param_2 = *param_1;
      *(long *)(param_2 + 2) = lVar15;
      local_51 = 1;
    }
  }
LAB_0094bd18:
  if (*DAT_01a1f100 != local_38) {
    uVar8 = thunk_FUN_012aa7f6();
    return uVar8;
  }
  return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),local_51);
}

