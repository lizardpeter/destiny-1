
void FUN_0057a260(int *param_1)

{
  int *piVar1;
  char cVar2;
  char cVar3;
  int iVar4;
  undefined4 uVar5;
  long lVar6;
  undefined8 uVar7;
  undefined4 *puVar8;
  int *piVar9;
  undefined4 local_178 [2];
  undefined4 local_170;
  char local_169 [9];
  undefined8 local_160 [6];
  long local_130;
  undefined1 local_128 [48];
  long local_f8;
  int local_f0 [20];
  undefined1 local_a0 [48];
  undefined1 local_70 [48];
  long local_40;
  undefined1 local_38 [8];
  long local_30;
  
  local_30 = *DAT_01a1f100;
  local_169[0] = '\0';
  cVar2 = FUN_002b3bd0(local_169);
  cVar3 = FUN_00b21030();
  local_40 = 0;
  if (local_169[0] == '\0') {
    if (cVar2 == '\0') goto LAB_0057a352;
    FUN_002b3bf0(local_a0,&local_40,local_70,local_f0,local_38);
    cVar2 = FUN_00244ee0(&local_f8);
    local_160[0] = 0;
    if (local_f8 != 0) {
      FUN_002447a0(&local_f8,local_128);
    }
    if (cVar2 != '\0') {
      cVar2 = FUN_002b82d0(local_70,local_128);
      if (cVar2 != '\0') goto LAB_0057a352;
    }
    thunk_FUN_012aa7c6(param_1 + 0x28,local_f0,0xbc);
    param_1[0x84] = 0;
    param_1[0x85] = 0;
    FUN_00784e60(0x110);
    local_40 = 0;
  }
  else {
    FUN_002b3bf0(param_1 + 0x6c,param_1 + 0x84,param_1 + 0x78,param_1 + 0x58,param_1 + 0x86);
LAB_0057a352:
    if (cVar3 != '\0') {
      if (*(long *)(param_1 + 0x84) == 0) {
        if (*(long *)(param_1 + 0x54) == 0) {
          local_160[0] = 0;
          if (local_40 == 0) goto LAB_0057a771;
          piVar9 = local_f0;
        }
        else {
          piVar9 = param_1 + 0x28;
        }
      }
      else {
        piVar9 = param_1 + 0x58;
      }
      local_160[0] = 0;
      cVar2 = FUN_00244ee0(&local_130);
      local_169[1] = '\0';
      local_169[2] = '\0';
      local_169[3] = '\0';
      local_169[4] = '\0';
      local_169[5] = '\0';
      local_169[6] = '\0';
      local_169[7] = '\0';
      local_169[8] = '\0';
      if (local_130 != 0) {
        FUN_002447a0(&local_130,local_160);
      }
      if (cVar2 != '\0') {
        cVar2 = FUN_002b82d0(piVar9 + 0x20,local_160);
        if (cVar2 != '\0') {
          piVar1 = piVar9 + 0x14;
          cVar2 = FUN_002b8450(piVar1);
          if (cVar2 == '\0') {
            if (*(char *)((long)param_1 + 6) != '\0') {
              uVar7 = FUN_00583cc0();
              FUN_00583b00(uVar7);
              *(undefined1 *)((long)param_1 + 6) = 0;
            }
            param_1[2] = 0;
            param_1[3] = 0;
            FUN_002b8260(param_1 + 4);
            *(undefined2 *)(param_1 + 0x23) = 0;
            param_1[0x22] = 0;
            param_1[0x20] = 0;
            param_1[0x21] = 0;
            param_1[0x1e] = 0;
            param_1[0x1f] = 0;
            param_1[0x1c] = 0;
            param_1[0x1d] = 0;
            param_1[0x1a] = 0;
            param_1[0x1b] = 0;
            param_1[0x18] = 0;
            param_1[0x19] = 0;
            param_1[0x16] = 0;
            param_1[0x17] = 0;
            param_1[0x14] = 0;
            param_1[0x15] = 0;
            param_1[0x12] = 0;
            param_1[0x13] = 0;
            param_1[0x10] = 0;
            param_1[0x11] = 0;
            *(undefined1 *)(param_1 + 1) = 0;
            *(undefined1 *)((long)param_1 + 5) = 0;
            param_1[0x26] = 1;
            FUN_00543ee0(param_1 + 0x24);
            *param_1 = 0;
          }
          else if (*param_1 == 0) {
            iVar4 = piVar9[0x2e];
            cVar2 = FUN_002b8450(piVar1);
            if (cVar2 != '\0') {
              if (*(char *)((long)param_1 + 6) != '\0') {
                uVar7 = FUN_00583cc0();
                FUN_00583b00(uVar7);
                *(undefined1 *)((long)param_1 + 6) = 0;
              }
              param_1[2] = 0;
              param_1[3] = 0;
              FUN_002b8260(param_1 + 4);
              *(undefined2 *)(param_1 + 0x23) = 0;
              param_1[0x22] = 0;
              param_1[0x20] = 0;
              param_1[0x21] = 0;
              param_1[0x1e] = 0;
              param_1[0x1f] = 0;
              param_1[0x1c] = 0;
              param_1[0x1d] = 0;
              param_1[0x1a] = 0;
              param_1[0x1b] = 0;
              param_1[0x18] = 0;
              param_1[0x19] = 0;
              param_1[0x16] = 0;
              param_1[0x17] = 0;
              param_1[0x14] = 0;
              param_1[0x15] = 0;
              param_1[0x12] = 0;
              param_1[0x13] = 0;
              param_1[0x10] = 0;
              param_1[0x11] = 0;
              *(undefined1 *)(param_1 + 1) = 0;
              *(undefined1 *)((long)param_1 + 5) = 0;
              param_1[0x26] = 1;
              FUN_00543ee0(param_1 + 0x24);
              uVar7 = *(undefined8 *)(piVar9 + 0x1c);
              *(undefined8 *)(param_1 + 0xe) = *(undefined8 *)(piVar9 + 0x1e);
              *(undefined8 *)(param_1 + 0xc) = uVar7;
              *(undefined8 *)(param_1 + 10) = *(undefined8 *)(piVar9 + 0x1a);
              *(undefined8 *)(param_1 + 8) = *(undefined8 *)(piVar9 + 0x18);
              uVar7 = *(undefined8 *)piVar1;
              *(undefined8 *)(param_1 + 6) = *(undefined8 *)(piVar9 + 0x16);
              *(undefined8 *)(param_1 + 4) = uVar7;
              param_1[0x26] = iVar4;
              param_1[0x88] = 0;
              param_1[0x89] = 0;
              *param_1 = 1;
              piVar9[0x2c] = 0;
              piVar9[0x2d] = 0;
              goto LAB_0057a771;
            }
          }
        }
      }
      piVar9[0x2c] = 0;
      piVar9[0x2d] = 0;
      goto LAB_0057a771;
    }
  }
  lVar6 = FUN_00587820();
  local_160[0] = 0;
  if (lVar6 == 0) {
    if (local_40 != 0) {
      thunk_FUN_012aa7c6(param_1 + 0x28,local_f0,0xbc);
    }
  }
  else if (local_40 == 0) {
    if ((*(long *)(param_1 + 0x84) != 0) || (local_160[0] = 0, *(long *)(param_1 + 0x54) != 0)) {
      local_160[0] = 0;
      lVar6 = FUN_00574ef0();
      if (*(char *)(lVar6 + 300) != '\0') {
        uVar7 = FUN_009503d0();
        local_178[0] = DAT_026bc320;
        uVar5 = FUN_00244e40();
        FUN_00950620(uVar7,local_178,uVar5,0);
        param_1[0x84] = 0;
        param_1[0x85] = 0;
        param_1[0x54] = 0;
        param_1[0x55] = 0;
      }
    }
  }
  else {
    lVar6 = FUN_00574ef0();
    if (*(char *)(lVar6 + 300) == '\0') {
      iVar4 = FUN_007850a0();
      puVar8 = &DAT_026bc328;
      if (0x23 < iVar4) {
        puVar8 = &DAT_026bc32c;
      }
    }
    else {
      puVar8 = &DAT_026bc320;
    }
    uVar5 = *puVar8;
    uVar7 = FUN_009503d0();
    local_170 = uVar5;
    uVar5 = FUN_00244e40();
    FUN_00950620(uVar7,&local_170,uVar5,0);
    local_40 = 0;
  }
LAB_0057a771:
  if (*DAT_01a1f100 == local_30) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

