
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

ulong FUN_0122c070(long param_1)

{
  char cVar1;
  undefined8 uVar2;
  ulong uVar3;
  ulong uVar4;
  long *plVar5;
  uint uVar6;
  undefined1 local_70 [8];
  undefined1 local_68 [16];
  undefined1 local_58 [8];
  undefined1 local_50 [8];
  undefined1 local_48 [16];
  long local_38;
  
  plVar5 = DAT_01a1f100;
  uVar6 = 0x2e1;
  local_38 = *DAT_01a1f100;
  if (*(char *)(param_1 + 0x225d) == '\0') {
    uVar6 = 700;
  }
  FUN_0122f4d0(local_48);
  cVar1 = FUN_0122f4f0(local_48,param_1 + 0x230c);
  uVar4 = 0x2de;
  if (cVar1 != '\0') {
    *(undefined1 *)(param_1 + 0x225c) = 1;
    thunk_FUN_012aa986(&DAT_02f66730,0,0x800);
    DAT_02f66f30 = 0;
    FUN_0123f1b0(0,s_info__016b7cec,s_bdAuth_016b7bf5,s_D__bungie_external_libraries_Dem_016b7bfc,
                 s_handleGetAccessTokenReply_016b8382,0x289,s_Received_access_token_reply_016b839c);
    FUN_012283a0(local_50);
    cVar1 = FUN_0122fec0(local_48,s_scope_016b83b8,local_50);
    uVar2 = FUN_01228c30(local_50);
    FUN_0123f1b0(0,s_info__016b7cec,s_bdAuth_016b7bf5,s_D__bungie_external_libraries_Dem_016b7bfc,
                 s_handleGetAccessTokenReply_016b8382,0x28f,
                 s_Received_reply_with_scope____s__016b83be,uVar2);
    FUN_012283a0(local_58);
    if ((cVar1 == '\0') ||
       (cVar1 = FUN_0122fec0(local_48,s_id_token_016b83de,local_58), cVar1 == '\0')) {
      cVar1 = '\0';
      FUN_0123f1b0(3,&DAT_016b7bf0,s_bdAuth_016b7bf5,s_D__bungie_external_libraries_Dem_016b7bfc,
                   s_handleGetAccessTokenReply_016b8382,0x2b7,
                   s_No_id_token_found_in_SCE_access__016b8442,uVar2);
      uVar4 = 0x2dd;
      plVar5 = DAT_01a1f100;
    }
    else {
      FUN_0123f1b0(1,s_message__016b7c82,s_bdAuth_016b7bf5,
                   s_D__bungie_external_libraries_Dem_016b7bfc,s_handleGetAccessTokenReply_016b8382,
                   0x297,s_Received_SCE_access_token_contai_016b83e7,uVar2);
      FUN_0122f4d0(local_68);
      FUN_01230490(local_68,s_scope_016b83b8,local_50);
      FUN_01230490(local_68,s_id_token_016b83de,local_58);
      FUN_012283a0(local_70);
      cVar1 = FUN_0122f550(local_68,local_70);
      if (cVar1 == '\0') {
        FUN_0123f1b0(3,&DAT_016b7bf0,s_bdAuth_016b7bf5,s_D__bungie_external_libraries_Dem_016b7bfc,
                     s_handleGetAccessTokenReply_016b8382,0x2b1,
                     s_Failed_to_serialize_JSON_openID_t_016b841c);
        uVar6 = 0x2de;
        plVar5 = DAT_01a1f100;
      }
      else {
        uVar2 = FUN_01228c30(local_70);
        uVar3 = thunk_FUN_012aa816(uVar2);
        uVar4 = 0x7ff;
        if (uVar3 < 0x7ff) {
          uVar4 = uVar3;
        }
        thunk_FUN_012aa7c6(&DAT_02f66730,uVar2,uVar4);
        (&DAT_02f66730)[uVar4] = 0;
        plVar5 = DAT_01a1f100;
        DAT_02f66f30 = *(char *)(param_1 + 0x225d) != '\0';
        if ((bool)DAT_02f66f30) {
          DAT_02f66f4c = *(undefined4 *)(FUN_00002280 + param_1);
        }
        DAT_02f66f48 = FUN_0123f7f0();
        DAT_02f66f41 = *(undefined4 *)(&DAT_00002274 + param_1);
        _DAT_02f66f31 = *(undefined8 *)(param_1 + 0x2264);
        uRam0000000002f66f39 = *(undefined8 *)((long)&DAT_0000226c + param_1);
      }
      FUN_012285a0(local_70);
      thunk_FUN_012312a0(local_68);
      uVar4 = (ulong)uVar6;
    }
    if ((*(char *)(param_1 + 0x225d) != '\0') &&
       ((*(undefined4 *)(param_1 + 0x2260) = 3, cVar1 == '\0' ||
        (cVar1 = FUN_01229a80(param_1), cVar1 == '\0')))) {
      FUN_0123f1b0(0,s_info__016b7cec,s_bdAuth_016b7bf5,s_D__bungie_external_libraries_Dem_016b7bfc,
                   s_handleGetAccessTokenReply_016b8382,0x2c2,
                   s_Failed_to_start_makeAuth_task_016b8468);
      uVar4 = (ulong)*(uint *)(param_1 + 0x1650);
    }
    FUN_012285a0(local_58);
    FUN_012285a0(local_50);
  }
  thunk_FUN_012312a0(local_48);
  if (*plVar5 != local_38) {
    uVar4 = thunk_FUN_012aa7f6();
    return uVar4;
  }
  return uVar4;
}

