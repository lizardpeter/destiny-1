
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0075d8e0(long param_1,int param_2)

{
  long lVar1;
  int iVar2;
  char cVar3;
  uint uVar4;
  long lVar5;
  undefined8 *puVar6;
  long lVar7;
  long lVar8;
  long lVar9;
  int iVar10;
  undefined8 uVar11;
  int *piVar12;
  int iVar13;
  int iVar14;
  undefined8 uVar15;
  uint local_190 [2];
  undefined8 local_188;
  undefined8 local_180;
  undefined1 local_178 [320];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  lVar5 = FUN_0075bdb0();
  puVar6 = (undefined8 *)FUN_00068570();
  local_180 = *puVar6;
  if ((*(uint *)(lVar5 + 0x8c48) < 0xb) && ((0x7f0U >> (*(uint *)(lVar5 + 0x8c48) & 0x1f) & 1) != 0)
     ) {
    lVar7 = FUN_00b74340(lVar5);
    lVar1 = lVar5 + 0x6eb8;
    cVar3 = FUN_00b8f690(lVar1);
    if (cVar3 != '\0') {
      cVar3 = FUN_00b8f690(lVar5 + 0x74e0);
      lVar8 = 0;
      if (cVar3 != '\0') {
        lVar8 = FUN_00b8e190(lVar5 + 0x74e0);
      }
      lVar9 = FUN_00b8f0c0(lVar1);
      local_188 = FUN_00b8f0f0(lVar1);
      local_190[0] = 0;
      FUN_00b8f120(lVar1,local_190);
      uVar4 = *(uint *)(lVar5 + 0x8c48);
      if ((((uVar4 & 0xfffffffe) != 6) && (uVar4 != 8)) && (uVar4 != 9)) {
        if ((lVar9 != lVar8) || (cVar3 = FUN_000b4f80(&local_188), cVar3 == '\0')) {
          iVar10 = FUN_000697a0();
          if (5000 < (uint)(iVar10 - _DAT_026c9898)) {
            cVar3 = FUN_000e4d70(3,2);
            if (cVar3 != '\0') {
              if ((DAT_026c98a0 == '\0') &&
                 (iVar10 = thunk_FUN_012aa7d6(&DAT_026c98a0), iVar10 != 0)) {
                DAT_026c989c = FUN_000e4a10(s_world_controller_activity_manage_0164ab6e);
                thunk_FUN_012aa7e6(&DAT_026c98a0);
              }
              FUN_01008290(local_178,s_world_controller_activity_manage_0164ab6e,
                           param_1 + 0x6c8 + (long)param_2 * 0x1f0);
              FUN_000e4aa0(DAT_026c989c,local_178);
            }
            _DAT_026c9898 = FUN_000697a0();
          }
          goto LAB_0075da85;
        }
        uVar4 = *(uint *)(lVar5 + 0x8c48);
      }
      if (((((uVar4 & 0xfffffffe) == 6) || (uVar4 == 8)) || (uVar4 == 9)) ||
         ((local_190[0] >> (*(uint *)(lVar7 + 0x5d0c) & 0x1f) & 1) != 0)) {
        iVar10 = -1;
        piVar12 = DAT_026c96f8;
        do {
          if (iVar10 == 1) {
            iVar10 = -1;
            break;
          }
          iVar10 = iVar10 + 1;
          iVar13 = *piVar12;
          piVar12 = piVar12 + 1;
        } while (iVar13 != param_2);
        piVar12 = DAT_026c96f8 + 2;
        iVar13 = -1;
        do {
          iVar14 = iVar10;
          if (iVar13 == 1) break;
          iVar13 = iVar13 + 1;
          iVar2 = *piVar12;
          piVar12 = piVar12 + 1;
          iVar14 = iVar13;
        } while (iVar2 != param_2);
        lVar5 = 0;
        do {
          uVar11 = 0xffffffff;
          if ((int)lVar5 == 2) break;
          uVar11 = 0;
          piVar12 = DAT_026c96f8 + lVar5;
          lVar5 = lVar5 + 1;
        } while (*piVar12 != param_2);
        lVar5 = 0;
        do {
          uVar15 = uVar11;
          if ((int)lVar5 == 2) break;
          lVar1 = lVar5 + 2;
          lVar5 = lVar5 + 1;
          uVar15 = 1;
        } while (DAT_026c96f8[lVar1] != param_2);
        lVar5 = (long)param_2 * 0x1f0;
        cVar3 = FUN_000b4f80(&local_188);
        if ((cVar3 != '\0') && (iVar10 = FUN_000697a0(), 5000 < (uint)(iVar10 - _DAT_026c98b8))) {
          cVar3 = FUN_000e4d70(3,2);
          if (cVar3 != '\0') {
            if ((DAT_026c98c0 == '\0') && (iVar10 = thunk_FUN_012aa7d6(&DAT_026c98c0), iVar10 != 0))
            {
              DAT_026c98bc = FUN_000e4a10(s_world_controller_activity_manage_0164ac40);
              thunk_FUN_012aa7e6(&DAT_026c98c0);
            }
            uVar11 = FUN_002a35d0(&local_188);
            FUN_01008290(local_178,s_world_controller_activity_manage_0164ac40,
                         param_1 + 0x6c8 + lVar5,uVar11,lVar9);
            FUN_000e4aa0(DAT_026c98bc,local_178);
          }
          _DAT_026c98b8 = FUN_000697a0();
        }
        *(int *)(param_1 + 0x6b8 + lVar5) = iVar14;
        cVar3 = FUN_00752150(3);
        if ((((cVar3 == '\0') || (iVar10 = FUN_0078b270(), iVar10 == 3)) ||
            (iVar10 = FUN_0078b250(), iVar10 == 3)) ||
           (cVar3 = FUN_00595470(param_1 + 0x640 + lVar5,local_188), cVar3 == '\0')) {
          iVar10 = FUN_000697a0();
          if (5000 < (uint)(iVar10 - _DAT_026c98d8)) {
            cVar3 = FUN_000e4d70(3,2);
            if (cVar3 != '\0') {
              if ((DAT_026c98e0 == '\0') &&
                 (iVar10 = thunk_FUN_012aa7d6(&DAT_026c98e0), iVar10 != 0)) {
                DAT_026c98dc = FUN_000e4a10(s_world_controller_activity_manage_0164acf1);
                thunk_FUN_012aa7e6(&DAT_026c98e0);
              }
              FUN_01008290(local_178,s_world_controller_activity_manage_0164acf1,
                           param_1 + 0x6c8 + lVar5);
              FUN_000e4aa0(DAT_026c98dc,local_178);
            }
            _DAT_026c98d8 = FUN_000697a0();
          }
        }
        else {
          FUN_00bb2420(param_2,iVar14,uVar15,&local_180);
          cVar3 = FUN_000e4d70(3,1);
          if (cVar3 != '\0') {
            if ((DAT_026c98d0 == '\0') && (iVar10 = thunk_FUN_012aa7d6(&DAT_026c98d0), iVar10 != 0))
            {
              DAT_026c98c8 = FUN_000e4a10(s_world_controller_activity_manage_0164ac94);
              thunk_FUN_012aa7e6(&DAT_026c98d0);
            }
            FUN_01008290(local_178,s_world_controller_activity_manage_0164ac94,
                         param_1 + 0x6c8 + lVar5);
            FUN_000e4aa0(DAT_026c98c8,local_178);
          }
          *(undefined1 *)(param_1 + 0x5bc + lVar5) = 1;
        }
      }
      else {
        iVar10 = FUN_000697a0();
        if (5000 < (uint)(iVar10 - _DAT_026c98a8)) {
          cVar3 = FUN_000e4d70(3,2);
          if (cVar3 != '\0') {
            if ((DAT_026c98b0 == '\0') && (iVar10 = thunk_FUN_012aa7d6(&DAT_026c98b0), iVar10 != 0))
            {
              DAT_026c98ac = FUN_000e4a10(s_world_controller_activity_manage_0164abbf);
              thunk_FUN_012aa7e6(&DAT_026c98b0);
            }
            FUN_01008290(local_178,s_world_controller_activity_manage_0164abbf,
                         param_1 + 0x6c8 + (long)param_2 * 0x1f0,*(undefined4 *)(lVar7 + 0x5d0c),
                         local_190[0]);
            FUN_000e4aa0(DAT_026c98ac,local_178);
          }
          _DAT_026c98a8 = FUN_000697a0();
        }
      }
      goto LAB_0075da85;
    }
  }
  iVar10 = FUN_000697a0();
  if (5000 < (uint)(iVar10 - _DAT_026c9888)) {
    cVar3 = FUN_000e4d70(3,2);
    if (cVar3 != '\0') {
      if ((DAT_026c9890 == '\0') && (iVar10 = thunk_FUN_012aa7d6(&DAT_026c9890), iVar10 != 0)) {
        DAT_026c988c = FUN_000e4a10(s_world_controller_activity_manage_0164ab1e);
        thunk_FUN_012aa7e6(&DAT_026c9890);
      }
      FUN_01008290(local_178,s_world_controller_activity_manage_0164ab1e,
                   param_1 + 0x6c8 + (long)param_2 * 0x1f0);
      FUN_000e4aa0(DAT_026c988c,local_178);
    }
    _DAT_026c9888 = FUN_000697a0();
  }
LAB_0075da85:
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

