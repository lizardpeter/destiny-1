
ulong FUN_007e2200(undefined8 param_1,long param_2,uint param_3)

{
  undefined8 *puVar1;
  long lVar2;
  uint uVar3;
  byte bVar4;
  byte bVar5;
  char cVar6;
  ulong uVar7;
  undefined8 in_XMM0_Qb;
  long local_60;
  byte local_3b [3];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  bVar4 = (byte)param_3;
  bVar5 = bVar4 >> 2 & 1;
  local_3b[0] = bVar4 >> 3 & 1;
  local_3b[1] = bVar4 >> 4 & 1;
  uVar7 = 0;
  local_3b[2] = bVar4 >> 5 & 1;
  local_60 = 0x9fc;
  do {
    uVar3 = *(uint *)(&DAT_000027c4 + uVar7 * 4 + param_2);
    if (((bVar5 == 0) || (uVar3 == 0)) || (DAT_026e2f94._2_1_ == '\0')) {
      if (uVar3 == 0) goto LAB_007e22bf;
    }
    else {
      lVar2 = (ulong)uVar3 * 0xe0 + 0x26f2438;
      cVar6 = FUN_00f82b70(lVar2);
      if ((cVar6 != '\0') &&
         (cVar6 = FUN_007e1ea0(param_1,param_2,lVar2,uVar7 & 0xffffffff), cVar6 != '\0')) {
        *(uint *)(param_2 + 0x27d8 + uVar7 * 4) = uVar3;
        puVar1 = (undefined8 *)(param_2 + local_60 * 4);
        *puVar1 = param_1;
        puVar1[1] = in_XMM0_Qb;
        (&DAT_026f248c)[(ulong)uVar3 * 0xe0] = 1;
LAB_007e22bf:
        param_3 = ~(4 << ((byte)uVar7 & 0x1f)) & param_3;
      }
    }
    if ((int)uVar7 == 3) {
      if (*DAT_01a1f100 != local_38) {
        uVar7 = thunk_FUN_012aa7f6();
        return uVar7;
      }
      return (ulong)param_3;
    }
    local_60 = local_60 + 4;
    bVar5 = local_3b[uVar7];
    uVar7 = uVar7 + 1;
  } while( true );
}

