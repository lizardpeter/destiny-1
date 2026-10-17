
void FUN_007a52d0(long param_1)

{
  uint uVar1;
  char cVar2;
  int iVar3;
  ulong uVar4;
  long lVar5;
  undefined8 uVar6;
  ulong uVar7;
  undefined1 local_160 [320];
  long local_20;
  
  local_20 = *DAT_01a1f100;
  iVar3 = *(int *)(param_1 + 0x6c4);
  switch(iVar3) {
  case 2:
  case 0xd:
  case 0xe:
  case 0x13:
  case 0x38:
  case 0x39:
  case 0x3f:
  case 0x40:
  case 0x41:
  case 0x42:
  case 0x79:
  case 0x7a:
  case 0x7b:
  case 0x7c:
  case 0x7d:
  case 0x7e:
  case 0x7f:
  case 0x80:
  case 0x81:
  case 0x82:
  case 0x83:
  case 0x84:
  case 0x85:
  case 0x86:
  case 0x87:
  case 0x88:
  case 0x89:
  case 0x8e:
  case 0x8f:
  case 0x90:
  case 0x91:
  case 0x92:
  case 0x93:
  case 0x94:
  case 0x95:
  case 0x96:
  case 0x97:
  case 0x98:
  case 0x99:
  case 0x9a:
  case 0x9b:
  case 0x9c:
  case 0x9d:
  case 0x9e:
  case 0x9f:
  case 0xa0:
  case 0xa1:
  case 0xa2:
  case 0xa3:
  case 0xa4:
  case 0xa5:
  case 0xa6:
  case 0xa7:
  case 0xa8:
  case 0xa9:
  case 0xaa:
  case 0xab:
  case 0xac:
  case 0xad:
  case 0xae:
  case 0xaf:
  case 0xb0:
  case 0xb1:
  case 0xb2:
  case 0xb3:
  case 0xb4:
  case 0xb5:
  case 0x110:
  case 0x111:
  case 0x112:
  case 0x113:
  case 0x114:
  case 0x115:
  case 0x117:
  case 0x11a:
  case 0x11b:
    *(ulong *)(param_1 + 0x6a0) = *(ulong *)(param_1 + 0x6a0) | 0x200606640c30;
    cVar2 = FUN_00752150(3);
    if (cVar2 != '\0') {
      *(ulong *)(param_1 + 0x6a0) = *(ulong *)(param_1 + 0x6a0) | 0x41ff800000000;
    }
    cVar2 = FUN_00752150(3);
    if ((cVar2 != '\0') || (cVar2 = FUN_00752150(1), cVar2 != '\0')) {
      *(undefined4 *)(param_1 + 0x6c8) = 4;
    }
    break;
  case 5:
  case 7:
  case 8:
    goto switchD_007a5310_caseD_5;
  case 9:
  case 0x12:
  case 0x3a:
  case 0x3b:
  case 0x3c:
  case 0x3d:
  case 0x3e:
  case 0x43:
  case 0x44:
  case 0x46:
  case 0x48:
  case 0x49:
  case 0x4a:
  case 0x4b:
  case 0x4c:
  case 0x4d:
  case 0x4e:
  case 0x4f:
  case 0x50:
  case 0x51:
  case 0x52:
  case 0x53:
  case 0x54:
  case 0x55:
  case 0x56:
  case 0x57:
  case 0x58:
  case 0x59:
  case 0x5a:
  case 0x5b:
  case 0x5c:
  case 0x5d:
  case 0x5e:
  case 0x5f:
  case 0x60:
  case 0x61:
  case 0x62:
  case 99:
  case 100:
  case 0x65:
  case 0x66:
  case 0x67:
  case 0x68:
  case 0x69:
  case 0x6a:
  case 0x6b:
  case 0x6c:
  case 0x6d:
  case 0x6e:
  case 0x6f:
  case 0x70:
  case 0x71:
  case 0x72:
  case 0x73:
  case 0x74:
  case 0x75:
  case 0x76:
  case 0x77:
  case 0x78:
  case 0xb6:
  case 0xb7:
  case 0xb8:
  case 0xb9:
  case 0xba:
  case 0xbb:
  case 0xbc:
  case 0xbd:
  case 0xbe:
  case 0xbf:
  case 0xc0:
  case 0xc1:
  case 0xc2:
  case 0xc3:
  case 0xc4:
  case 0xc5:
  case 0xc6:
  case 199:
  case 200:
  case 0xc9:
  case 0xca:
  case 0xcb:
  case 0xcc:
  case 0xcd:
  case 0xce:
  case 0xcf:
  case 0xd0:
  case 0xd1:
  case 0xd2:
  case 0xd3:
  case 0xd4:
  case 0xd5:
  case 0xd6:
  case 0xd7:
  case 0xd8:
  case 0xd9:
  case 0xda:
  case 0xdb:
  case 0xdc:
  case 0xdd:
  case 0xde:
  case 0xdf:
  case 0xe0:
  case 0xe1:
  case 0xe2:
  case 0xe3:
  case 0xe4:
  case 0xe5:
  case 0xe6:
  case 0xe7:
  case 0xe8:
  case 0xe9:
  case 0xea:
  case 0xeb:
  case 0xec:
  case 0xed:
  case 0xee:
  case 0xef:
  case 0xf0:
  case 0xf1:
  case 0xf2:
  case 0xf3:
  case 0xf4:
  case 0xf5:
  case 0xf6:
  case 0xf7:
  case 0xf8:
  case 0xf9:
  case 0xfa:
  case 0xfb:
  case 0xfc:
  case 0xfd:
  case 0xfe:
  case 0xff:
  case 0x100:
  case 0x101:
  case 0x102:
  case 0x103:
  case 0x104:
  case 0x105:
  case 0x106:
  case 0x107:
  case 0x108:
  case 0x109:
  case 0x10a:
  case 0x10b:
  case 0x10c:
  case 0x10d:
  case 0x10e:
  case 0x10f:
  case 0x116:
    if ((*(uint *)(param_1 + 0x6dc) & 0xfffff) == 0) {
      *(byte *)(param_1 + 0x6a0) = *(byte *)(param_1 + 0x6a0) | 0x10;
    }
  case 0:
  case 3:
  case 4:
  case 6:
  case 10:
  case 0x10:
  case 0x11:
  case 0x14:
  case 0x15:
  case 0x16:
  case 0x17:
  case 0x18:
  case 0x19:
  case 0x1a:
  case 0x1b:
  case 0x1c:
  case 0x1d:
  case 0x1e:
  case 0x1f:
  case 0x20:
  case 0x21:
  case 0x22:
  case 0x23:
  case 0x24:
  case 0x25:
  case 0x26:
  case 0x27:
  case 0x28:
  case 0x29:
  case 0x2a:
  case 0x2b:
  case 0x2c:
  case 0x2d:
  case 0x2e:
  case 0x2f:
  case 0x30:
  case 0x31:
  case 0x32:
  case 0x33:
  case 0x34:
  case 0x35:
  case 0x36:
  case 0x37:
  case 0x47:
  case 0x118:
  case 0x119:
    *(byte *)(param_1 + 0x6a1) = *(byte *)(param_1 + 0x6a1) | 4;
switchD_007a5310_caseD_5:
    uVar4 = *(ulong *)(param_1 + 0x6a0) | 0x1000000000800;
    *(ulong *)(param_1 + 0x6a0) = uVar4;
    if ((1 < iVar3 - 3U) && (iVar3 != 0x118)) {
LAB_007a53f4:
      uVar4 = uVar4 | 0x400040600000;
      *(ulong *)(param_1 + 0x6a0) = uVar4;
    }
    *(ulong *)(param_1 + 0x6a0) = uVar4 | 0x40;
    cVar2 = FUN_00752150(3);
    if (cVar2 != '\0') {
      *(byte *)(param_1 + 0x6a6) = *(byte *)(param_1 + 0x6a6) | 2;
    }
    *(undefined4 *)(param_1 + 0x6c8) = 0x1a;
    break;
  case 0xc:
    *(ulong *)(param_1 + 0x6a0) = *(ulong *)(param_1 + 0x6a0) | 0x4400860640c30;
    *(undefined4 *)(param_1 + 0x6c8) = 0x14;
    break;
  case 0xf:
    uVar4 = *(ulong *)(param_1 + 0x6a0);
    goto LAB_007a53f4;
  case 0x8a:
  case 0x8b:
  case 0x8c:
  case 0x8d:
    *(byte *)(param_1 + 0x6a5) = *(byte *)(param_1 + 0x6a5) | 0x34;
    *(undefined4 *)(param_1 + 0x6c8) = 4;
  }
  cVar2 = FUN_00752150(3);
  if (cVar2 != '\0') {
    lVar5 = FUN_005753c0(4);
    uVar1 = *(uint *)(param_1 + 0x6c4);
    if ((((uVar1 != 0xffffffff) && (0xf < uVar1)) && ((uVar1 - 0x10 < 0x108 || (uVar1 != 0x119))))
       && (((((*(uint *)(param_1 + 0x6c8) | 0x10) != 0x14 && (cVar2 = FUN_005428c0(), lVar5 != 0))
            && (cVar2 == '\x01')) && (cVar2 = FUN_00546f20(lVar5), cVar2 != '\0')))) {
      cVar2 = FUN_0025cc10();
      if (cVar2 != '\0') {
        FUN_00552e10();
      }
      *(undefined8 *)(param_1 + 0x6b0) = 0;
      *(undefined8 *)(param_1 + 0x6a8) = 0;
      *(undefined8 *)(param_1 + 0x6a0) = 0;
      *(undefined8 *)(param_1 + 0x6a0) = 0x4400860640c30;
      *(undefined4 *)(param_1 + 0x6c8) = 0x14;
    }
  }
  if ((*(ulong *)(param_1 + 0x6a0) & 0x400) == 0) {
    *(ulong *)(param_1 + 0x6a0) = *(ulong *)(param_1 + 0x6a0) | 0x3000;
  }
  iVar3 = *(int *)(param_1 + 0x6c4);
  if (((1 < iVar3 - 5U) && (iVar3 != 0)) && (iVar3 != 0x119)) {
    uVar6 = FUN_00574ef0();
    thunk_FUN_01018280(uVar6);
  }
  lVar5 = FUN_0034e3c0();
  if ((*(char *)(lVar5 + 0xe8) == '\0') || (*(char *)(param_1 + 0x70d) == '\0')) {
    *(byte *)(param_1 + 0x6a0) = *(byte *)(param_1 + 0x6a0) | 2;
  }
  else {
    cVar2 = FUN_000e4d70(5,2);
    if (cVar2 != '\0') {
      if ((DAT_026d0148 == '\0') && (iVar3 = thunk_FUN_012aa7d6(&DAT_026d0148), iVar3 != 0)) {
        DAT_026d0140 = FUN_000e4a10(s_world_controller_state_cleanup__N_0165bdac);
        thunk_FUN_012aa7e6(&DAT_026d0148);
      }
      FUN_01008290(local_160,s_world_controller_state_cleanup__N_0165bdac);
      FUN_000e4aa0(DAT_026d0140,local_160);
    }
  }
  uVar4 = *(ulong *)(param_1 + 0x6a0);
  *(ulong *)(param_1 + 0x6a0) = uVar4 | 0x80000000438c;
  iVar3 = *(int *)(param_1 + 0x6c4);
  if (iVar3 == 4) {
LAB_007a5643:
    *(int *)(param_1 + 0x6cc) = iVar3;
  }
  else if (iVar3 == 3) {
    *(ulong *)(param_1 + 0x6a0) = uVar4 | 0x80001800438d;
    *(undefined4 *)(param_1 + 0x6cc) = 3;
  }
  else {
    uVar7 = 0x8000009a438c;
    if (iVar3 == 8) {
      uVar7 = 0x8000011a438c;
    }
    *(ulong *)(param_1 + 0x6a0) = uVar4 | uVar7 | 0x18018001;
    if ((iVar3 - 5U < 2) || (iVar3 == 0x119)) goto LAB_007a5643;
    *(undefined4 *)(param_1 + 0x6cc) = 0;
  }
  iVar3 = *(int *)(param_1 + 0x6c8);
  FUN_000c19e0(param_1);
  if (iVar3 == 0x1a) {
    uVar6 = 0x14;
LAB_007a5676:
    FUN_007591a0(param_1,uVar6);
  }
  else if (iVar3 == 0x14) {
    uVar6 = 0x13;
    goto LAB_007a5676;
  }
  uVar1 = *(uint *)(param_1 + 0x6c4);
  if (((uVar1 != 0xffffffff) && (0xf < uVar1)) && ((uVar1 - 0x10 < 0x108 || (uVar1 != 0x119)))) {
    iVar3 = *(int *)(param_1 + 0x6c8);
    if (iVar3 == 0x1a) {
      FUN_0078b340();
      if (((*(byte *)(param_1 + 0x6a3) & 0x80) == 0) && (cVar2 = FUN_00752150(3), cVar2 != '\0')) {
        *(byte *)(param_1 + 0x6a3) = *(byte *)(param_1 + 0x6a3) | 0x80;
        *(undefined4 *)(param_1 + 0x6c0) = 2;
      }
      uVar6 = 1;
    }
    else {
      if (iVar3 == 0x14) {
        FUN_0078b340();
        if (((*(byte *)(param_1 + 0x6a3) & 0x80) == 0) && (cVar2 = FUN_00752150(3), cVar2 != '\0'))
        {
          *(ulong *)(param_1 + 0x6a0) = *(ulong *)(param_1 + 0x6a0) | 0x180000000;
          *(undefined4 *)(param_1 + 0x6c0) = 1;
        }
      }
      else {
        if (iVar3 != 4) goto LAB_007a5806;
        if ((DAT_026d0158 == '\0') && (iVar3 = thunk_FUN_012aa7d6(&DAT_026d0158), iVar3 != 0)) {
          DAT_026d0150 = FUN_000e4a10(s_world_controller_state_cleanup_k_0165be28);
          thunk_FUN_012aa7e6(&DAT_026d0158);
        }
        uVar6 = FUN_00783960(*(undefined4 *)(param_1 + 0x6c4));
        FUN_01008290(local_160,s_world_controller_state_cleanup_k_0165be28,uVar6);
        FUN_000e4aa0(DAT_026d0150,local_160);
        FUN_0078b2f0(*(undefined4 *)(param_1 + 0x6c4));
        if (((*(byte *)(param_1 + 0x6a3) & 0x80) == 0) && (cVar2 = FUN_00752150(3), cVar2 != '\0'))
        {
          cVar2 = FUN_00752a20();
          if ((cVar2 == '\0') || (cVar2 = FUN_007e9a60(), cVar2 != '\0')) {
            *(ulong *)(param_1 + 0x6a0) = *(ulong *)(param_1 + 0x6a0) | 0x180000000;
          }
          FUN_0094fe00(0);
          *(undefined4 *)(param_1 + 0x6c0) = 0;
        }
      }
      uVar6 = 0;
    }
    FUN_0078b170(uVar6);
  }
LAB_007a5806:
  cVar2 = FUN_0078c710();
  if ((cVar2 == '\0') || (1 < *(int *)(param_1 + 0x6c4) - 7U)) {
    FUN_0078c540();
  }
  *(undefined1 *)(param_1 + 0x6b9) = 1;
  if ((DAT_026d0168 == '\0') && (iVar3 = thunk_FUN_012aa7d6(&DAT_026d0168), iVar3 != 0)) {
    DAT_026d0160 = FUN_000e4a10(s_world_controller_state_cleanup__R_0165be74);
    thunk_FUN_012aa7e6(&DAT_026d0168);
  }
  FUN_01008290(local_160,s_world_controller_state_cleanup__R_0165be74,
               *(undefined8 *)(param_1 + 0x6a0));
  FUN_000e4aa0(DAT_026d0160,local_160);
  if (*DAT_01a1f100 == local_20) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

