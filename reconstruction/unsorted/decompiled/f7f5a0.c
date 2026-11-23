
void FUN_00f7f5a0(long param_1,uint *param_2,int param_3)

{
  char cVar1;
  uint *puVar2;
  uint uVar3;
  
  uVar3 = param_3 + 2;
  puVar2 = *(uint **)(param_1 + 0x10);
  if ((uint)((ulong)(*(long *)(param_1 + 8) - (long)puVar2) >> 2) < uVar3) {
    cVar1 = (**(code **)(param_1 + 0x18))(param_1,uVar3,*(undefined8 *)(param_1 + 0x20));
    if (cVar1 == '\0') {
      return;
    }
    puVar2 = *(uint **)(param_1 + 0x10);
  }
  *puVar2 = param_3 << 0x10 | 0xc0006900;
  puVar2[1] = 0x191;
  switch(param_3) {
  case 0x20:
    puVar2[0x21] = param_2[0x1f];
  case 0x1f:
    puVar2[0x20] = param_2[0x1e];
  case 0x1e:
    puVar2[0x1f] = param_2[0x1d];
  case 0x1d:
    puVar2[0x1e] = param_2[0x1c];
  case 0x1c:
    puVar2[0x1d] = param_2[0x1b];
  case 0x1b:
    puVar2[0x1c] = param_2[0x1a];
  case 0x1a:
    puVar2[0x1b] = param_2[0x19];
  case 0x19:
    puVar2[0x1a] = param_2[0x18];
  case 0x18:
    puVar2[0x19] = param_2[0x17];
  case 0x17:
    puVar2[0x18] = param_2[0x16];
  case 0x16:
    puVar2[0x17] = param_2[0x15];
  case 0x15:
    puVar2[0x16] = param_2[0x14];
  case 0x14:
    puVar2[0x15] = param_2[0x13];
  case 0x13:
    puVar2[0x14] = param_2[0x12];
  case 0x12:
    puVar2[0x13] = param_2[0x11];
  case 0x11:
    puVar2[0x12] = param_2[0x10];
  case 0x10:
    puVar2[0x11] = param_2[0xf];
  case 0xf:
    puVar2[0x10] = param_2[0xe];
  case 0xe:
    puVar2[0xf] = param_2[0xd];
  case 0xd:
    puVar2[0xe] = param_2[0xc];
  case 0xc:
    puVar2[0xd] = param_2[0xb];
  case 0xb:
    puVar2[0xc] = param_2[10];
  case 10:
    puVar2[0xb] = param_2[9];
  case 9:
    puVar2[10] = param_2[8];
  case 8:
    puVar2[9] = param_2[7];
  case 7:
    puVar2[8] = param_2[6];
  case 6:
    puVar2[7] = param_2[5];
  case 5:
    puVar2[6] = param_2[4];
  case 4:
    puVar2[5] = param_2[3];
  case 3:
    puVar2[4] = param_2[2];
  case 2:
    puVar2[3] = param_2[1];
  case 1:
    puVar2[2] = *param_2;
  default:
    *(uint **)(param_1 + 0x10) = puVar2 + uVar3;
    return;
  }
}

