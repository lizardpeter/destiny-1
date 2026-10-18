
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00ba6830(undefined8 *param_1,int *param_2,undefined8 param_3,long param_4)

{
  uint *puVar1;
  long *plVar2;
  undefined *puVar3;
  bool bVar4;
  bool bVar5;
  char cVar6;
  int iVar7;
  int iVar8;
  undefined4 uVar9;
  long lVar10;
  long *plVar11;
  undefined8 uVar12;
  undefined8 uVar13;
  long lVar14;
  long *plVar15;
  uint uVar16;
  uint uVar17;
  int *piVar18;
  ulong uVar19;
  long lVar20;
  uint uVar21;
  char *pcVar22;
  ulong uVar23;
  uint local_284;
  undefined8 local_230;
  char local_225;
  uint local_224;
  long local_220;
  undefined1 local_218 [320];
  long alStack_d8 [20];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  iVar7 = FUN_00bb58c0(*param_1);
  uVar23 = 0;
  uVar13 = 0;
  if (iVar7 != -1) {
    lVar10 = FUN_00bb54d0(*param_1,iVar7);
    uVar13 = 0;
    if (lVar10 != 0) {
      uVar13 = FUN_0075f130(*(undefined8 *)(lVar10 + 0x10));
    }
  }
  lVar10 = FUN_00b74340(uVar13);
  piVar18 = (int *)(lVar10 + 0x5c);
  do {
    if (((*(uint *)(lVar10 + 0x2c) >> ((uint)uVar23 & 0x1f) & 1) != 0) && (*piVar18 != 3)) {
      plVar11 = (long *)FUN_00b81740(lVar10,uVar23 & 0xffffffff);
      alStack_d8[uVar23] = *plVar11;
    }
    piVar18 = piVar18 + 0x5a;
    uVar23 = uVar23 + 1;
  } while ((int)uVar23 != 0x14);
  puVar1 = (uint *)(param_1 + 2);
  uVar23 = 0;
  do {
    if (((*(uint *)(&DAT_00001c54 + lVar10) >> ((uint)uVar23 & 0x1f) & 1) != 0) &&
       ((((1 << ((byte)uVar23 & 0x1f) & *puVar1) == 0 ||
         (*(char *)(param_1 + uVar23 * 0x1d + 4) != '\0')) ||
        (param_1[uVar23 * 0x1d + 3] != *(long *)(&DAT_00001c5c + uVar23 * 0xe8 + lVar10))))) {
      uVar16 = 0;
      plVar11 = param_1 + 3;
      do {
        if ((((*puVar1 >> (uVar16 & 0x1f) & 1) != 0) && ((char)plVar11[1] == '\0')) &&
           (*plVar11 == *(long *)(&DAT_00001c5c + uVar23 * 0xe8 + lVar10))) {
          iVar7 = *param_2;
          iVar8 = iVar7 + 1;
          *param_2 = iVar8;
          uVar19 = param_4 + 7 + (long)iVar7 * 0x108 & 0xfffffffffffffff8;
          if (uVar19 != 0) {
            thunk_FUN_012aa986(uVar19 + 0x40,0,0x90);
            *(undefined1 *)(uVar19 + 0x9a) = 0xff;
            *(undefined8 *)(uVar19 + 0xf0) = 0;
            *(undefined8 *)(uVar19 + 0xe8) = 0;
            *(undefined8 *)(uVar19 + 0xe0) = 0;
            *(undefined8 *)(uVar19 + 0xd8) = 0;
            *(undefined8 *)(uVar19 + 0xd0) = 0;
            *(undefined4 *)(uVar19 + 0xd0) = 0xffffffff;
            iVar8 = *param_2;
          }
          FUN_00ba9100(param_4 + 7 + (long)(iVar8 + -1) * 0x108 & 0xfffffffffffffff8,puVar1,uVar16,
                       uVar23 & 0xffffffff);
          break;
        }
        plVar11 = plVar11 + 0x1d;
        uVar16 = uVar16 + 1;
      } while ((int)uVar16 < 0x14);
    }
    uVar23 = uVar23 + 1;
  } while ((int)uVar23 != 0x14);
  plVar11 = (long *)(&DAT_00001c5c + lVar10);
  uVar23 = 0;
  do {
    if (((*(uint *)(param_1 + 2) >> ((uint)uVar23 & 0x1f) & 1) != 0) &&
       (lVar14 = uVar23 * 0xe8, *(char *)(param_1 + uVar23 * 0x1d + 4) == '\0')) {
      plVar2 = param_1 + uVar23 * 0x1d + 3;
      plVar15 = plVar11;
      uVar16 = 0;
      if (((1 << ((byte)uVar23 & 0x1f) & *(uint *)(&DAT_00001c54 + lVar10)) == 0) ||
         (((uVar16 = 0, *plVar2 != *(long *)(&DAT_00001c5c + lVar14 + lVar10) ||
           (param_1[uVar23 * 0x1d + 5] != alStack_d8[*(int *)(&DAT_00001c64 + lVar14 + lVar10)])) ||
          (uVar16 = 0, *(int *)((long)param_1 + lVar14 + 0x34) != *(int *)(lVar10 + 0x1c74 + lVar14)
          )))) {
        do {
          if (((*(uint *)(&DAT_00001c54 + lVar10) >> (uVar16 & 0x1f) & 1) != 0) &&
             (*plVar15 == *plVar2)) goto LAB_00ba6c60;
          uVar16 = uVar16 + 1;
          plVar15 = plVar15 + 0x1d;
        } while ((int)uVar16 < 0x14);
        iVar7 = *param_2;
        iVar8 = iVar7 + 1;
        *param_2 = iVar8;
        uVar19 = param_4 + 7 + (long)iVar7 * 0x108 & 0xfffffffffffffff8;
        if (uVar19 != 0) {
          thunk_FUN_012aa986(uVar19 + 0x40,0,0x90);
          *(undefined1 *)(uVar19 + 0x9a) = 0xff;
          *(undefined8 *)(uVar19 + 0xf0) = 0;
          *(undefined8 *)(uVar19 + 0xe8) = 0;
          *(undefined8 *)(uVar19 + 0xe0) = 0;
          *(undefined8 *)(uVar19 + 0xd8) = 0;
          *(undefined8 *)(uVar19 + 0xd0) = 0;
          *(undefined4 *)(uVar19 + 0xd0) = 0xffffffff;
          iVar8 = *param_2;
        }
        FUN_00ba90d0(param_4 + 7 + (long)(iVar8 + -1) * 0x108 & 0xfffffffffffffff8,puVar1,
                     uVar23 & 0xffffffff,plVar2,0);
        cVar6 = FUN_00bb6b20(*param_1,uVar23 & 0xffffffff,0);
        if (cVar6 != '\0') {
          FUN_00bb6aa0(*param_1,uVar23 & 0xffffffff);
        }
      }
    }
LAB_00ba6c60:
    uVar23 = uVar23 + 1;
  } while ((int)uVar23 != 0x14);
  uVar16 = 0;
  uVar23 = 0;
  local_284 = 0;
  do {
    uVar17 = 1 << ((byte)uVar23 & 0x1f);
    if ((*(uint *)(&DAT_00001c54 + lVar10) >> ((uint)uVar23 & 0x1f) & 1) != 0) {
      cVar6 = FUN_0025cc10();
      if (cVar6 == '\0') {
LAB_00ba6dc0:
        if (((*puVar1 & uVar17) == 0) || (*(char *)(param_1 + uVar23 * 0x1d + 4) != '\0')) {
          lVar14 = uVar23 * 0xe8;
          puVar3 = &DAT_00001c5c + lVar14 + lVar10;
          local_220 = -1;
          FUN_0075f210();
          if ((local_220 == 0) ||
             ((local_220 == -1 || (bVar4 = false, *(int *)(lVar10 + 0x1c74 + lVar14) != -1)))) {
            bVar4 = local_220 != -1 && local_220 != 0;
          }
          plVar11 = alStack_d8 + *(int *)(&DAT_00001c64 + lVar14 + lVar10);
          bVar5 = bVar4;
          if (bVar4) {
            uVar21 = 0;
            pcVar22 = (char *)(param_1 + 4);
            do {
              if (((((*puVar1 >> (uVar21 & 0x1f) & 1) != 0) && (*pcVar22 == '\0')) &&
                  (*(long *)(pcVar22 + 8) == *plVar11)) &&
                 (bVar5 = false, *(int *)(pcVar22 + 0x14) == *(int *)(lVar10 + 0x1c74 + lVar14)))
              break;
              pcVar22 = pcVar22 + 0xe8;
              uVar21 = uVar21 + 1;
              bVar5 = bVar4;
            } while ((int)uVar21 < 0x14);
            iVar7 = 0;
            lVar20 = (long)param_1 + 0x123c;
            do {
              if (0x13 < iVar7) goto LAB_00ba6f43;
              cVar6 = FUN_000685a0(lVar20,plVar11);
              iVar7 = iVar7 + 1;
              lVar20 = lVar20 + 8;
            } while (cVar6 == '\0');
          }
          if (bVar5) {
            uVar12 = FUN_00244270(lVar10 + 0x1ce8 + lVar14,puVar3);
            FUN_00ba7440(puVar1,uVar23 & 0xffffffff,puVar3,uVar12,lVar10 + 0x1ce0 + lVar14,
                         &local_224,&local_225);
            if ((local_224 != 0xffffffff) && (local_224 != (uint)uVar23)) {
              iVar7 = *param_2;
              iVar8 = iVar7 + 1;
              *param_2 = iVar8;
              uVar19 = param_4 + 7 + (long)iVar7 * 0x108 & 0xfffffffffffffff8;
              if (uVar19 != 0) {
                thunk_FUN_012aa986(uVar19 + 0x40,0,0x90);
                *(undefined1 *)(uVar19 + 0x9a) = 0xff;
                *(undefined8 *)(uVar19 + 0xf0) = 0;
                *(undefined8 *)(uVar19 + 0xe8) = 0;
                *(undefined8 *)(uVar19 + 0xe0) = 0;
                *(undefined8 *)(uVar19 + 0xd8) = 0;
                *(undefined8 *)(uVar19 + 0xd0) = 0;
                *(undefined4 *)(uVar19 + 0xd0) = 0xffffffff;
                iVar8 = *param_2;
              }
              FUN_00ba9100(param_4 + 7 + (long)(iVar8 + -1) * 0x108 & 0xfffffffffffffff8,puVar1,
                           uVar23 & 0xffffffff,local_224);
            }
            if (local_225 != '\0') {
              iVar7 = *param_2;
              iVar8 = iVar7 + 1;
              *param_2 = iVar8;
              uVar19 = param_4 + 7 + (long)iVar7 * 0x108 & 0xfffffffffffffff8;
              if (uVar19 != 0) {
                thunk_FUN_012aa986(uVar19 + 0x40,0,0x90);
                *(undefined1 *)(uVar19 + 0x9a) = 0xff;
                *(undefined8 *)(uVar19 + 0xf0) = 0;
                *(undefined8 *)(uVar19 + 0xe8) = 0;
                *(undefined8 *)(uVar19 + 0xe0) = 0;
                *(undefined8 *)(uVar19 + 0xd8) = 0;
                *(undefined8 *)(uVar19 + 0xd0) = 0;
                *(undefined4 *)(uVar19 + 0xd0) = 0xffffffff;
                iVar8 = *param_2;
              }
              FUN_00ba9170(param_4 + 7 + (long)(iVar8 + -1) * 0x108 & 0xfffffffffffffff8,puVar1,
                           uVar23 & 0xffffffff);
            }
            local_230 = *(undefined8 *)
                         (lVar10 + 0x160 + (long)*(int *)(&DAT_00001c64 + lVar14 + lVar10) * 0x168);
            cVar6 = FUN_000b4f80(&local_230);
            if (cVar6 == '\0') {
              local_284 = local_284 | uVar17;
            }
            else {
              iVar7 = *param_2;
              iVar8 = iVar7 + 1;
              *param_2 = iVar8;
              uVar19 = param_4 + 7 + (long)iVar7 * 0x108 & 0xfffffffffffffff8;
              if (uVar19 != 0) {
                thunk_FUN_012aa986(uVar19 + 0x40,0,0x90);
                *(undefined1 *)(uVar19 + 0x9a) = 0xff;
                *(undefined8 *)(uVar19 + 0xf0) = 0;
                *(undefined8 *)(uVar19 + 0xe8) = 0;
                *(undefined8 *)(uVar19 + 0xe0) = 0;
                *(undefined8 *)(uVar19 + 0xd8) = 0;
                *(undefined8 *)(uVar19 + 0xd0) = 0;
                *(undefined4 *)(uVar19 + 0xd0) = 0xffffffff;
                iVar8 = *param_2;
              }
              FUN_00ba91a0(param_4 + 7 + (long)(iVar8 + -1) * 0x108 & 0xfffffffffffffff8,puVar1,
                           uVar23 & 0xffffffff,puVar3,plVar11,local_220,&local_230,
                           *(undefined4 *)(&DAT_00001c68 + lVar14 + lVar10),
                           *(undefined4 *)(lVar10 + 0x1c74 + lVar14),lVar10 + 0x1c78 + lVar14,1);
            }
          }
          else {
LAB_00ba6f43:
            local_284 = local_284 | uVar17;
          }
        }
        else {
          lVar14 = lVar10 + 0x1c78 + uVar23 * 0xe8;
          iVar7 = thunk_FUN_012aa826(lVar14,param_1 + uVar23 * 0x1d + 9,0xb8);
          if (iVar7 != 0) {
            iVar7 = *param_2;
            iVar8 = iVar7 + 1;
            *param_2 = iVar8;
            uVar19 = param_4 + 7 + (long)iVar7 * 0x108 & 0xfffffffffffffff8;
            if (uVar19 != 0) {
              thunk_FUN_012aa986(uVar19 + 0x40,0,0x90);
              *(undefined1 *)(uVar19 + 0x9a) = 0xff;
              *(undefined8 *)(uVar19 + 0xf0) = 0;
              *(undefined8 *)(uVar19 + 0xe8) = 0;
              *(undefined8 *)(uVar19 + 0xe0) = 0;
              *(undefined8 *)(uVar19 + 0xd8) = 0;
              *(undefined8 *)(uVar19 + 0xd0) = 0;
              *(undefined4 *)(uVar19 + 0xd0) = 0xffffffff;
              iVar8 = *param_2;
            }
            FUN_00ba92f0(param_4 + 7 + (long)(iVar8 + -1) * 0x108 & 0xfffffffffffffff8,puVar1,
                         uVar23 & 0xffffffff,&DAT_00001c5c + uVar23 * 0xe8 + lVar10,lVar14);
          }
        }
      }
      else {
        if (*(long *)(lVar10 + 0x1ce0 + uVar23 * 0xe8) == 0) {
          if ((param_1[uVar23 * 0x1d + 0x16] != 0) &&
             (iVar7 = FUN_000697a0(), 1000 < (uint)(iVar7 - _DAT_028a5fe0))) {
            cVar6 = FUN_000e4d70(0x10,2);
            if (cVar6 != '\0') {
              if ((DAT_028a5fe8 == '\0') && (iVar7 = thunk_FUN_012aa7d6(&DAT_028a5fe8), iVar7 != 0))
              {
                DAT_028a5fe4 = FUN_000e4a10(s__networking_simulation_membershi_016974ff + 1);
                thunk_FUN_012aa7e6(&DAT_028a5fe8);
              }
              FUN_01008290(local_218,s__networking_simulation_membershi_016974ff + 1,
                           uVar23 & 0xffffffff);
              FUN_000e4aa0(DAT_028a5fe4,local_218);
            }
            _DAT_028a5fe0 = FUN_000697a0();
            uVar16 = uVar17 | uVar16;
            goto LAB_00ba73b0;
          }
        }
        else if (*(long *)(lVar10 + 0x1ce8 + uVar23 * 0xe8) != 0) goto LAB_00ba6dc0;
        uVar16 = uVar17 | uVar16;
      }
    }
LAB_00ba73b0:
    uVar23 = uVar23 + 1;
    if ((int)uVar23 == 0x14) {
      FUN_00b9b720(puVar1);
      if (((local_284 & 0xfffff) == 0) && ((uVar16 & 0xfffff) == 0)) {
        uVar9 = FUN_00b74390(uVar13);
        *(undefined4 *)((long)param_1 + 0xc) = uVar9;
      }
      if (*DAT_01a1f100 != local_38) {
        thunk_FUN_012aa7f6();
        return;
      }
      return;
    }
  } while( true );
}

