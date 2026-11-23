
undefined8 FUN_0029c710(long *param_1,int *param_2)

{
  long *plVar1;
  long *plVar2;
  long lVar3;
  char cVar4;
  char cVar5;
  char cVar6;
  int iVar7;
  undefined4 uVar8;
  undefined4 uVar9;
  undefined8 uVar10;
  undefined8 uVar11;
  undefined1 uVar12;
  undefined *puVar13;
  undefined *puVar14;
  undefined1 local_178 [320];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  if (DAT_026554f8 == '\0') {
    iVar7 = thunk_FUN_012aa7d6(&DAT_026554f8);
    if (iVar7 != 0) {
      DAT_026554f0 = FUN_000e4a10(s_networking_activity_client_recei_0162249d);
      thunk_FUN_012aa7e6(&DAT_026554f8);
    }
  }
  cVar4 = (**(code **)(*(long *)param_1[0x1ca] + 0x18))();
  cVar5 = (**(code **)(*param_1 + 0x18))(param_1);
  cVar6 = (**(code **)(*param_1 + 0x18))(param_1);
  puVar13 = &DAT_01621de5;
  if (cVar4 != '\0') {
    puVar13 = &DAT_01621de3;
  }
  plVar1 = param_1 + 4;
  puVar14 = &DAT_01621de5;
  if (cVar5 != '\0') {
    puVar14 = &DAT_01621de3;
  }
  if (cVar6 == '\0') {
    uVar10 = FUN_00001df0();
  }
  else {
    uVar10 = (**(code **)(*param_1 + 0x10))(param_1);
  }
  plVar2 = param_1 + 0x1ce;
  uVar8 = FUN_00057e60();
  uVar11 = FUN_002a35d0(param_2 + 2);
  FUN_01008290(local_178,s_networking_activity_client_recei_0162249d,plVar1,puVar13,puVar14,uVar10,
               uVar8,uVar11,*param_2,(int)(char)param_2[0x40],(long)param_2 + 0x101,
               (char)param_2[0x65]);
  uVar8 = (undefined4)((ulong)uVar11 >> 0x20);
  FUN_000e4aa0(DAT_026554f0,local_178);
  if ((*(byte *)(param_1 + 0x26) & 8) == 0) {
    if (DAT_02655508 == '\0') {
      iVar7 = thunk_FUN_012aa7d6(&DAT_02655508);
      if (iVar7 != 0) {
        DAT_02655500 = FUN_000e4a10(s_networking_activity_client_recei_01622557);
        thunk_FUN_012aa7e6(&DAT_02655508);
      }
    }
    cVar4 = (**(code **)(*(long *)param_1[0x1ca] + 0x18))();
    cVar5 = (**(code **)(*param_1 + 0x18))(param_1);
    cVar6 = (**(code **)(*param_1 + 0x18))(param_1);
    puVar13 = &DAT_01621de5;
    puVar14 = &DAT_01621de5;
    if (cVar4 != '\0') {
      puVar14 = &DAT_01621de3;
    }
    if (cVar5 != '\0') {
      puVar13 = &DAT_01621de3;
    }
    if (cVar6 == '\0') {
      uVar10 = FUN_00001df0();
    }
    else {
      uVar10 = (**(code **)(*param_1 + 0x10))(param_1);
    }
    uVar9 = FUN_00057e60(plVar2);
    uVar12 = 0;
    FUN_01008290(local_178,s_networking_activity_client_recei_01622557,plVar1,puVar14,puVar13,uVar10
                 ,uVar9,CONCAT44(uVar8,(int)(char)param_2[0x40]));
    FUN_000e4aa0(DAT_02655500,local_178);
  }
  else {
    if (*param_2 == (int)param_1[0x173]) {
      if ((char)param_2[0x40] == '\0') {
        param_1[0x193] = *(long *)(param_2 + 2);
        thunk_FUN_012aa7c6(param_1 + 0x194,param_2,0x1a8);
        *(uint *)(param_1 + 0xd8e) = (uint)*(ushort *)((long)param_2 + 0x196);
        *(uint *)((long)param_1 + 0x6c74) = (uint)*(ushort *)(param_2 + 0x66);
        FUN_00298e70(param_1,(long)param_1 + 0xda1,*(undefined4 *)((long)param_1 + 0xe2c));
        *(byte *)(param_1 + 0x26) = *(byte *)(param_1 + 0x26) | 0x20;
        (**(code **)(*param_1 + 0x28))(param_1);
        uVar8 = *(undefined4 *)((long)param_1 + 0x1c);
        lVar3 = param_1[3];
        uVar10 = (**(code **)(*param_1 + 0x10))(param_1);
        FUN_00240a00((int)lVar3,uVar8,uVar10,param_2);
      }
      else {
        if (DAT_02655528 == '\0') {
          iVar7 = thunk_FUN_012aa7d6(&DAT_02655528);
          if (iVar7 != 0) {
            DAT_02655520 = FUN_000e4a10(s_networking_activity_client_recei_0162267d);
            thunk_FUN_012aa7e6(&DAT_02655528);
          }
        }
        cVar4 = (**(code **)(*(long *)param_1[0x1ca] + 0x18))();
        cVar5 = (**(code **)(*param_1 + 0x18))(param_1);
        cVar6 = (**(code **)(*param_1 + 0x18))(param_1);
        puVar13 = &DAT_01621de5;
        puVar14 = &DAT_01621de5;
        if (cVar4 != '\0') {
          puVar14 = &DAT_01621de3;
        }
        if (cVar5 != '\0') {
          puVar13 = &DAT_01621de3;
        }
        if (cVar6 == '\0') {
          uVar10 = FUN_00001df0();
        }
        else {
          uVar10 = (**(code **)(*param_1 + 0x10))(param_1);
        }
        uVar8 = FUN_00057e60(plVar2);
        uVar11 = FUN_000e9fa0((int)(char)param_2[0x40]);
        FUN_01008290(local_178,s_networking_activity_client_recei_0162267d,plVar1,puVar14,puVar13,
                     uVar10,uVar8,uVar11);
        FUN_000e4aa0(DAT_02655520,local_178);
      }
      *(byte *)(param_1 + 0x26) = *(byte *)(param_1 + 0x26) | 0x10;
    }
    else {
      if (DAT_02655518 == '\0') {
        iVar7 = thunk_FUN_012aa7d6(&DAT_02655518);
        if (iVar7 != 0) {
          DAT_02655510 = FUN_000e4a10(s_networking_activity_client_recei_016225f3);
          thunk_FUN_012aa7e6(&DAT_02655518);
        }
      }
      cVar4 = (**(code **)(*(long *)param_1[0x1ca] + 0x18))();
      cVar5 = (**(code **)(*param_1 + 0x18))(param_1);
      cVar6 = (**(code **)(*param_1 + 0x18))(param_1);
      puVar13 = &DAT_01621de5;
      puVar14 = &DAT_01621de5;
      if (cVar4 != '\0') {
        puVar14 = &DAT_01621de3;
      }
      if (cVar5 != '\0') {
        puVar13 = &DAT_01621de3;
      }
      if (cVar6 == '\0') {
        uVar10 = FUN_00001df0();
      }
      else {
        uVar10 = (**(code **)(*param_1 + 0x10))(param_1);
      }
      uVar9 = FUN_00057e60(plVar2);
      FUN_01008290(local_178,s_networking_activity_client_recei_016225f3,plVar1,puVar14,puVar13,
                   uVar10,uVar9,CONCAT44(uVar8,*param_2),(int)param_1[0x173]);
      FUN_000e4aa0(DAT_02655510,local_178);
    }
    uVar12 = 1;
  }
  if (*DAT_01a1f100 == local_38) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),uVar12);
  }
  uVar10 = thunk_FUN_012aa7f6();
  return uVar10;
}

