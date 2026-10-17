
void FUN_00b0dd60(char *param_1)

{
  undefined8 uVar1;
  char cVar2;
  char cVar3;
  int iVar4;
  undefined4 uVar5;
  undefined8 uVar6;
  long lVar7;
  char *pcVar8;
  undefined4 uVar9;
  undefined8 in_stack_fffffffffffff970;
  undefined1 *puVar10;
  char local_678 [256];
  undefined1 local_578 [1024];
  undefined1 local_178 [320];
  long local_38;
  
  uVar9 = (undefined4)((ulong)in_stack_fffffffffffff970 >> 0x20);
  local_38 = *DAT_01a1f100;
  cVar2 = FUN_000e4d70(6,1);
  if (cVar2 != '\0') {
    cVar2 = *param_1;
    cVar3 = FUN_000e4d70(6,1);
    if (cVar2 == '\0') {
      if (cVar3 == '\0') goto LAB_00b0e80a;
      if (DAT_028029e0 == '\0') {
        iVar4 = thunk_FUN_012aa7d6(&DAT_028029e0);
        if (iVar4 != 0) {
          DAT_028029d8 = FUN_000e4a10(s_networking_configuration__config_01684515);
          thunk_FUN_012aa7e6(&DAT_028029e0);
        }
      }
      FUN_01008290(local_178,s_networking_configuration__config_01684515);
      uVar9 = DAT_028029d8;
    }
    else {
      if (cVar3 != '\0') {
        if (DAT_02802900 == '\0') {
          iVar4 = thunk_FUN_012aa7d6(&DAT_02802900);
          if (iVar4 != 0) {
            DAT_028028f8 = FUN_000e4a10(s_networking_configuration_dump____01683e20);
            thunk_FUN_012aa7e6(&DAT_02802900);
          }
        }
        if (*(int *)(param_1 + 0x28) == -1) {
          pcVar8 = s_PRIVATE_0164c995;
        }
        else {
          pcVar8 = s_PUBLIC_0164c99d;
        }
        FUN_01008290(local_178,s_networking_configuration_dump____01683e20,pcVar8);
        FUN_000e4aa0(DAT_028028f8,local_178);
      }
      cVar2 = FUN_000e4d70(6,1);
      if (cVar2 != '\0') {
        if (DAT_02802910 == '\0') {
          iVar4 = thunk_FUN_012aa7d6(&DAT_02802910);
          if (iVar4 != 0) {
            DAT_02802908 = FUN_000e4a10(s_networking_configuration_dump__g_01683e4d);
            thunk_FUN_012aa7e6(&DAT_02802910);
          }
        }
        uVar9 = *(undefined4 *)(param_1 + 4);
        uVar6 = FUN_00079a30(&DAT_01620037,*(undefined4 *)(param_1 + 0xc));
        uVar5 = FUN_00057e60(param_1 + 0x28);
        cVar2 = param_1[0x38];
        uVar1 = *(undefined8 *)(param_1 + 0x30);
        local_578[0] = 0;
        if ((byte)param_1[0x39] < 2) {
          if ((param_1[0x39] & 1U) != 0) {
            local_678[0] = '\0';
            FUN_0100a3d0(local_678,&DAT_0160ec9c,0);
            lVar7 = 0;
            do {
              if (local_678[lVar7] == '|') {
                local_678[lVar7] = '.';
              }
              lVar7 = lVar7 + 1;
            } while ((int)lVar7 != 0x40);
            FUN_00065140(local_578,local_678,0x400);
          }
        }
        else {
          FUN_00065030(local_578,s_flags_invalid_0164c8f5,0x400);
        }
        puVar10 = local_578;
        FUN_01008290(local_178,s_networking_configuration_dump__g_01683e4d,uVar9,uVar6,uVar5,uVar1,
                     cVar2,puVar10);
        uVar9 = (undefined4)((ulong)puVar10 >> 0x20);
        FUN_000e4aa0(DAT_02802908,local_178);
      }
      cVar2 = FUN_000e4d70(6,1);
      if (cVar2 != '\0') {
        if (DAT_02802920 == '\0') {
          iVar4 = thunk_FUN_012aa7d6(&DAT_02802920);
          if (iVar4 != 0) {
            DAT_02802918 = FUN_000e4a10(s_networking_configuration_dump____01683ee7);
            thunk_FUN_012aa7e6(&DAT_02802920);
          }
        }
        FUN_01008290((double)*(float *)(param_1 + 0x48),(double)*(float *)(param_1 + 0x4c),
                     (double)*(float *)(param_1 + 0x50),local_178,
                     s_networking_configuration_dump____01683ee7,param_1[0x3a],
                     *(undefined4 *)(param_1 + 0x44),*(undefined4 *)(param_1 + 0x54));
        FUN_000e4aa0(DAT_02802918,local_178);
      }
      cVar2 = FUN_000e4d70(6,1);
      if (cVar2 != '\0') {
        if (DAT_02802930 == '\0') {
          iVar4 = thunk_FUN_012aa7d6(&DAT_02802930);
          if (iVar4 != 0) {
            DAT_02802928 = FUN_000e4a10(s_networking_configuration_dump____01683f4e);
            thunk_FUN_012aa7e6(&DAT_02802930);
          }
        }
        FUN_01008290(local_178,s_networking_configuration_dump____01683f4e,
                     *(undefined4 *)(param_1 + 0x58),*(undefined4 *)(param_1 + 0x5c),param_1[100],
                     param_1[0x65]);
        FUN_000e4aa0(DAT_02802928,local_178);
      }
      cVar2 = FUN_000e4d70(6,1);
      if (cVar2 != '\0') {
        if (DAT_02802940 == '\0') {
          iVar4 = thunk_FUN_012aa7d6(&DAT_02802940);
          if (iVar4 != 0) {
            DAT_02802938 = FUN_000e4a10(s_networking_configuration_dump____01684005);
            thunk_FUN_012aa7e6(&DAT_02802940);
          }
        }
        FUN_01008290(local_178,s_networking_configuration_dump____01684005,
                     *(undefined4 *)(param_1 + 0x68));
        FUN_000e4aa0(DAT_02802938,local_178);
      }
      cVar2 = FUN_000e4d70(6,1);
      if (cVar2 != '\0') {
        if (DAT_02802950 == '\0') {
          iVar4 = thunk_FUN_012aa7d6(&DAT_02802950);
          if (iVar4 != 0) {
            DAT_02802948 = FUN_000e4a10(s_networking_configuration_dump____01684055);
            thunk_FUN_012aa7e6(&DAT_02802950);
          }
        }
        FUN_01008290(local_178,s_networking_configuration_dump____01684055,
                     *(undefined4 *)(param_1 + 0x6c),*(undefined4 *)(param_1 + 0x70),
                     *(undefined4 *)(param_1 + 0x74));
        FUN_000e4aa0(DAT_02802948,local_178);
      }
      cVar2 = FUN_000e4d70(6,1);
      if (cVar2 != '\0') {
        if (DAT_02802960 == '\0') {
          iVar4 = thunk_FUN_012aa7d6(&DAT_02802960);
          if (iVar4 != 0) {
            DAT_02802958 = FUN_000e4a10(s_networking_configuration_dump__l_016840df);
            thunk_FUN_012aa7e6(&DAT_02802960);
          }
        }
        FUN_01008290((double)*(float *)(param_1 + 0x84),local_178,
                     s_networking_configuration_dump__l_016840df,0,*(undefined4 *)(param_1 + 0x7c),
                     *(undefined4 *)(param_1 + 0x80));
        FUN_000e4aa0(DAT_02802958,local_178);
      }
      cVar2 = FUN_000e4d70(6,1);
      if (cVar2 != '\0') {
        if (DAT_02802960 == '\0') {
          iVar4 = thunk_FUN_012aa7d6(&DAT_02802960);
          if (iVar4 != 0) {
            DAT_02802958 = FUN_000e4a10(s_networking_configuration_dump__l_016840df);
            thunk_FUN_012aa7e6(&DAT_02802960);
          }
        }
        FUN_01008290((double)*(float *)(param_1 + 0x90),local_178,
                     s_networking_configuration_dump__l_016840df,1,*(undefined4 *)(param_1 + 0x88),
                     *(undefined4 *)(param_1 + 0x8c));
        FUN_000e4aa0(DAT_02802958,local_178);
      }
      cVar2 = FUN_000e4d70(6,1);
      if (cVar2 != '\0') {
        if (DAT_02802970 == '\0') {
          iVar4 = thunk_FUN_012aa7d6(&DAT_02802970);
          if (iVar4 != 0) {
            DAT_02802968 = FUN_000e4a10(s_networking_configuration_dump____0168414a);
            thunk_FUN_012aa7e6(&DAT_02802970);
          }
        }
        FUN_01008290(local_178,s_networking_configuration_dump____0168414a,
                     *(undefined4 *)(param_1 + 0x94),*(undefined4 *)(param_1 + 0x98),
                     *(undefined4 *)(param_1 + 0x9c),*(undefined4 *)(param_1 + 0xa0));
        FUN_000e4aa0(DAT_02802968,local_178);
      }
      cVar2 = FUN_000e4d70(6,1);
      if (cVar2 != '\0') {
        if (DAT_02802980 == '\0') {
          iVar4 = thunk_FUN_012aa7d6(&DAT_02802980);
          if (iVar4 != 0) {
            DAT_02802978 = FUN_000e4a10(s_networking_configuration_dump____016841d8);
            thunk_FUN_012aa7e6(&DAT_02802980);
          }
        }
        FUN_01008290(local_178,s_networking_configuration_dump____016841d8,
                     *(undefined4 *)(param_1 + 0xa4),*(undefined4 *)(param_1 + 0xac),
                     *(undefined4 *)(param_1 + 0xb0),*(undefined4 *)(param_1 + 0xb4));
        FUN_000e4aa0(DAT_02802978,local_178);
      }
      cVar2 = FUN_000e4d70(6,1);
      if (cVar2 != '\0') {
        if (DAT_02802990 == '\0') {
          iVar4 = thunk_FUN_012aa7d6(&DAT_02802990);
          if (iVar4 != 0) {
            DAT_02802988 = FUN_000e4a10(s_networking_configuration_dump__t_0168426d);
            thunk_FUN_012aa7e6(&DAT_02802990);
          }
        }
        FUN_01008290(local_178,s_networking_configuration_dump__t_0168426d,(int)param_1[0xbc],
                     *(undefined4 *)(param_1 + 0xc0),*(undefined4 *)(param_1 + 0xc4),
                     *(undefined4 *)(param_1 + 0x128),(int)param_1[300],
                     CONCAT44(uVar9,(int)param_1[0x12d]));
        FUN_000e4aa0(DAT_02802988,local_178);
      }
      local_678[0] = '\0';
      FUN_01009470(local_678,s__min__d_max__d_allegiance__d__01684312,*(undefined4 *)(param_1 + 200)
                   ,*(undefined4 *)(param_1 + 0xcc),(int)param_1[0xd0]);
      FUN_01009470(local_678,s__min__d_max__d_allegiance__d__01684312,
                   *(undefined4 *)(param_1 + 0xd4),*(undefined4 *)(param_1 + 0xd8),
                   (int)param_1[0xdc]);
      FUN_01009470(local_678,s__min__d_max__d_allegiance__d__01684312,
                   *(undefined4 *)(param_1 + 0xe0),*(undefined4 *)(param_1 + 0xe4),
                   (int)param_1[0xe8]);
      FUN_01009470(local_678,s__min__d_max__d_allegiance__d__01684312,
                   *(undefined4 *)(param_1 + 0xec),*(undefined4 *)(param_1 + 0xf0),
                   (int)param_1[0xf4]);
      FUN_01009470(local_678,s__min__d_max__d_allegiance__d__01684312,
                   *(undefined4 *)(param_1 + 0xf8),*(undefined4 *)(param_1 + 0xfc),
                   (int)param_1[0x100]);
      FUN_01009470(local_678,s__min__d_max__d_allegiance__d__01684312,
                   *(undefined4 *)(param_1 + 0x104),*(undefined4 *)(param_1 + 0x108),
                   (int)param_1[0x10c]);
      FUN_01009470(local_678,s__min__d_max__d_allegiance__d__01684312,
                   *(undefined4 *)(param_1 + 0x110),*(undefined4 *)(param_1 + 0x114),
                   (int)param_1[0x118]);
      FUN_01009470(local_678,s__min__d_max__d_allegiance__d__01684312,
                   *(undefined4 *)(param_1 + 0x11c),*(undefined4 *)(param_1 + 0x120),
                   (int)param_1[0x124]);
      cVar2 = FUN_000e4d70(6,1);
      if (cVar2 != '\0') {
        if (DAT_028029a0 == '\0') {
          iVar4 = thunk_FUN_012aa7d6(&DAT_028029a0);
          if (iVar4 != 0) {
            DAT_02802998 = FUN_000e4a10(s_networking_configuration_dump__t_01684330);
            thunk_FUN_012aa7e6(&DAT_028029a0);
          }
        }
        FUN_01008290(local_178,s_networking_configuration_dump__t_01684330,local_678);
        FUN_000e4aa0(DAT_02802998,local_178);
      }
      cVar2 = FUN_000e4d70(6,1);
      if (cVar2 != '\0') {
        if (DAT_028029b0 == '\0') {
          iVar4 = thunk_FUN_012aa7d6(&DAT_028029b0);
          if (iVar4 != 0) {
            DAT_028029a8 = FUN_000e4a10(s_networking_configuration_dump____01684365);
            thunk_FUN_012aa7e6(&DAT_028029b0);
          }
        }
        FUN_01008290((double)*(float *)(param_1 + 0x13c),(double)*(float *)(param_1 + 0x144),
                     local_178,s_networking_configuration_dump____01684365,
                     *(undefined4 *)(param_1 + 0x134));
        FUN_000e4aa0(DAT_028029a8,local_178);
      }
      cVar2 = FUN_000e4d70(6,1);
      if (cVar2 != '\0') {
        if (DAT_028029c0 == '\0') {
          iVar4 = thunk_FUN_012aa7d6(&DAT_028029c0);
          if (iVar4 != 0) {
            DAT_028029b8 = FUN_000e4a10(s_networking_configuration_dump__w_016843c9);
            thunk_FUN_012aa7e6(&DAT_028029c0);
          }
        }
        FUN_01008290((double)*(float *)(param_1 + 0x14c),(double)*(float *)(param_1 + 0x150),
                     (double)*(float *)(param_1 + 0x154),(double)*(float *)(param_1 + 0x158),
                     (double)*(float *)(param_1 + 0x15c),(double)*(float *)(param_1 + 0x160),
                     local_178,s_networking_configuration_dump__w_016843c9);
        FUN_000e4aa0(DAT_028029b8,local_178);
      }
      cVar2 = FUN_000e4d70(6,1);
      if (cVar2 == '\0') goto LAB_00b0e80a;
      if (DAT_028029d0 == '\0') {
        iVar4 = thunk_FUN_012aa7d6(&DAT_028029d0);
        if (iVar4 != 0) {
          DAT_028029c8 = FUN_000e4a10(s_networking_configuration_dump____01684486);
          thunk_FUN_012aa7e6(&DAT_028029d0);
        }
      }
      FUN_01008290((double)*(float *)(param_1 + 0x140),(double)*(float *)(param_1 + 0x148),local_178
                   ,s_networking_configuration_dump____01684486,*(undefined4 *)(param_1 + 0x138));
      uVar9 = DAT_028029c8;
    }
    FUN_000e4aa0(uVar9,local_178);
  }
LAB_00b0e80a:
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

