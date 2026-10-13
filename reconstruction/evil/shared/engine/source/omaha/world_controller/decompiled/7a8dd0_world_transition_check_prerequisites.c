
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

ulong FUN_007a8dd0(long param_1)

{
  undefined4 uVar1;
  char cVar2;
  undefined1 uVar3;
  undefined1 uVar4;
  undefined1 uVar5;
  short sVar6;
  int iVar7;
  undefined8 uVar8;
  long *plVar9;
  int *piVar10;
  long lVar11;
  char *pcVar12;
  undefined8 uVar13;
  ulong uVar14;
  undefined4 *puVar15;
  uint uVar16;
  undefined8 unaff_R15;
  undefined4 local_1930 [2];
  undefined1 local_1928 [1616];
  undefined1 local_12d8;
  undefined1 local_1258;
  undefined1 local_1257;
  undefined1 local_1256;
  undefined1 local_1255;
  undefined1 local_1254;
  undefined1 local_1253;
  undefined1 local_1252;
  undefined4 local_1250;
  undefined1 local_124c;
  undefined8 local_1248;
  undefined1 local_1240;
  undefined1 local_1238 [4601];
  undefined1 local_3f;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  uVar8 = FUN_003409a0();
  sVar6 = FUN_0078df40();
  uVar14 = CONCAT62((int6)((ulong)unaff_R15 >> 0x10),sVar6);
  cVar2 = FUN_0025cc10();
  piVar10 = (int *)0x0;
  if (cVar2 != '\0') {
    plVar9 = (long *)FUN_0025a550();
    piVar10 = (int *)(**(code **)(*plVar9 + 0x38))(plVar9);
  }
  uVar16 = 2;
  if (((*(byte *)(param_1 + 0x6d0) & 1) == 0) && (uVar16 = 1, (*(byte *)(param_1 + 0x6c8) & 1) == 0)
     ) {
    uVar16 = (*(uint *)(param_1 + 0x6c0) & 1) - 1;
  }
  plVar9 = (long *)FUN_005753c0(4);
  if (plVar9 == (long *)0x0) {
LAB_007a8e8a:
    cVar2 = FUN_005505a0(uVar14 & 0xffffffff);
    if (cVar2 != '\0') {
      cVar2 = FUN_000e4d70(5,4);
      if (cVar2 != '\0') {
        if (DAT_026d0450 == '\0') {
          iVar7 = thunk_FUN_012aa7d6(&DAT_026d0450);
          if (iVar7 != 0) {
            DAT_026d0448 = FUN_000e4a10(s_world_controller_state_setup_act_0165d1d5);
            thunk_FUN_012aa7e6(&DAT_026d0450);
          }
        }
        pcVar12 = s_<unknown>_0165d580;
        if ((piVar10 != (int *)0x0) && ((ulong)(long)sVar6 < (ulong)(long)*piVar10)) {
          puVar15 = (undefined4 *)
                    ((long)piVar10 + (long)sVar6 * 0x10 + *(long *)(piVar10 + 2) + 0x18);
          if (puVar15 != (undefined4 *)0x0) {
            pcVar12 = (char *)FUN_00079a30(&DAT_01620037,*puVar15);
          }
        }
        FUN_01008290(local_1930,s_world_controller_state_setup_act_0165d1d5,pcVar12,(int)sVar6);
        FUN_000e4aa0(DAT_026d0448,local_1930);
      }
      FUN_00783ee0(0x19,0x17,s_World_transition_requires_DLC__0165d265);
      goto LAB_007a93d5;
    }
    if (plVar9 != (long *)0x0) {
      cVar2 = FUN_00547ef0(plVar9,uVar14 & 0xffffffff);
      if (cVar2 == '\0') {
        cVar2 = FUN_000e4d70(5,4);
        if (cVar2 != '\0') {
          if (DAT_026d0460 == '\0') {
            iVar7 = thunk_FUN_012aa7d6(&DAT_026d0460);
            if (iVar7 != 0) {
              DAT_026d0458 = FUN_000e4a10(s_world_controller_state_setup_act_0165d284);
              thunk_FUN_012aa7e6(&DAT_026d0460);
            }
          }
          pcVar12 = s_<unknown>_0165d580;
          if ((piVar10 != (int *)0x0) && ((ulong)(long)sVar6 < (ulong)(long)*piVar10)) {
            puVar15 = (undefined4 *)
                      ((long)piVar10 + (long)sVar6 * 0x10 + *(long *)(piVar10 + 2) + 0x18);
            if (puVar15 != (undefined4 *)0x0) {
              pcVar12 = (char *)FUN_00079a30(&DAT_01620037,*puVar15);
            }
          }
          FUN_01008290(local_1930,s_world_controller_state_setup_act_0165d284,pcVar12,(int)sVar6);
          FUN_000e4aa0(DAT_026d0458,local_1930);
        }
        FUN_00783ee0(0x19,0x18,s_World_transition_requires_permis_0165d30d);
        goto LAB_007a93d5;
      }
    }
  }
  else {
    cVar2 = (**(code **)(*plVar9 + 0x58))(plVar9);
    if (cVar2 == '\0') goto LAB_007a8e8a;
    lVar11 = (**(code **)(*plVar9 + 0x10))(plVar9);
    if (*(char *)(lVar11 + 0x714c) == '\0') goto LAB_007a8e8a;
  }
  if (uVar16 == 0) {
    cVar2 = FUN_000e4d70(5,2);
    if (cVar2 != '\0') {
      if (DAT_026d0470 == '\0') {
        iVar7 = thunk_FUN_012aa7d6(&DAT_026d0470);
        if (iVar7 != 0) {
          DAT_026d0468 = FUN_000e4a10(s_world_controller_state_setup_act_0165d334);
          thunk_FUN_012aa7e6(&DAT_026d0470);
        }
      }
      FUN_01008290(local_1930,s_world_controller_state_setup_act_0165d334);
      FUN_000e4aa0(DAT_026d0468,local_1930);
    }
    FUN_007a9880(param_1);
    FUN_01052740(local_1930);
    uVar8 = *(undefined8 *)(param_1 + 0x688);
    uVar1 = *(undefined4 *)(param_1 + 0x680);
    uVar3 = FUN_00763710();
    uVar4 = FUN_00001f70();
    uVar5 = FUN_0075c670(param_1 + 0x658);
    local_1930[0] = 0x18f8;
    thunk_FUN_012aa7c6(local_1928,param_1 + 0x30,0x650);
    local_1258 = 0;
    local_12d8 = 0;
    thunk_FUN_012aa986(local_1238,0,0x11f9);
    local_1257 = 1;
    local_1256 = 0;
    local_1255 = 0;
    local_124c = 1;
    local_1240 = 1;
    local_3f = 0;
    local_1254 = uVar3;
    local_1253 = uVar4;
    local_1252 = uVar5;
    local_1250 = uVar1;
    local_1248 = uVar8;
    uVar8 = FUN_0034cbb0();
    FUN_0034c8e0(uVar8,3,local_1930);
    uVar16 = 1;
  }
  else {
    uVar13 = FUN_0034cbb0();
    cVar2 = FUN_0034c9a0(uVar13,3);
    if (cVar2 == '\0') {
      cVar2 = FUN_0034d120();
      if (cVar2 == '\0') {
        cVar2 = FUN_00340cb0(uVar8);
        if (cVar2 == '\0') {
          cVar2 = FUN_000e4d70(5,4);
          if (cVar2 != '\0') {
            if (DAT_026d0490 == '\0') {
              iVar7 = thunk_FUN_012aa7d6(&DAT_026d0490);
              if (iVar7 != 0) {
                DAT_026d0488 = FUN_000e4a10(s_world_controller_state_setup_act_0165d3ee);
                thunk_FUN_012aa7e6(&DAT_026d0490);
              }
            }
            FUN_01008290(local_1930,s_world_controller_state_setup_act_0165d3ee);
            FUN_000e4aa0(DAT_026d0488,local_1930);
          }
          pcVar12 = s_Transition_completed__but_we_don_0165d462;
        }
        else {
          uVar13 = FUN_003409a0();
          lVar11 = FUN_00078970(uVar13);
          if (lVar11 != 0) {
            iVar7 = thunk_FUN_012aab16(param_1 + 0x658,lVar11,0x28);
            if (iVar7 == 0) {
              cVar2 = FUN_000e4d70(5,2);
              if (cVar2 != '\0') {
                if (DAT_026d04b0 == '\0') {
                  iVar7 = thunk_FUN_012aa7d6(&DAT_026d04b0);
                  if (iVar7 != 0) {
                    DAT_026d04a8 = FUN_000e4a10(s_world_controller_state_setup_act_0165d52c);
                    thunk_FUN_012aa7e6(&DAT_026d04b0);
                  }
                }
                FUN_01008290(local_1930,s_world_controller_state_setup_act_0165d52c);
                FUN_000e4aa0(DAT_026d04a8,local_1930);
              }
              FUN_007a9b40();
              lVar11 = FUN_00078970(uVar8);
              if (lVar11 != 0) {
                FUN_00078970(uVar8);
              }
              FUN_007636d0();
              FUN_00777550(6);
              uVar16 = 2;
              goto LAB_007a93d5;
            }
          }
          cVar2 = FUN_000e4d70(5,4);
          if (cVar2 != '\0') {
            if (DAT_026d04a0 == '\0') {
              iVar7 = thunk_FUN_012aa7d6(&DAT_026d04a0);
              if (iVar7 != 0) {
                DAT_026d0498 = FUN_000e4a10(s_world_controller_state_setup_act_0165d49e);
                thunk_FUN_012aa7e6(&DAT_026d04a0);
              }
            }
            FUN_01008290(local_1930,s_world_controller_state_setup_act_0165d49e);
            FUN_000e4aa0(DAT_026d0498,local_1930);
          }
          pcVar12 = s_Transition_completed__but_was_no_0165d501;
        }
        FUN_00783ee0(0x19,0x37,pcVar12);
        goto LAB_007a93d5;
      }
    }
    iVar7 = FUN_000697a0();
    if (1000 < (uint)(iVar7 - _DAT_026d0478)) {
      cVar2 = FUN_000e4d70(5,1);
      if (cVar2 != '\0') {
        if (DAT_026d0480 == '\0') {
          iVar7 = thunk_FUN_012aa7d6(&DAT_026d0480);
          if (iVar7 != 0) {
            DAT_026d047c = FUN_000e4a10(s_world_controller_state_setup_act_0165d388);
            thunk_FUN_012aa7e6(&DAT_026d0480);
          }
        }
        FUN_01008290(local_1930,s_world_controller_state_setup_act_0165d388);
        FUN_000e4aa0(DAT_026d047c,local_1930);
      }
      _DAT_026d0478 = FUN_000697a0();
    }
  }
LAB_007a93d5:
  if (*DAT_01a1f100 == local_38) {
    return (ulong)uVar16;
  }
  uVar14 = thunk_FUN_012aa7f6();
  return uVar14;
}

