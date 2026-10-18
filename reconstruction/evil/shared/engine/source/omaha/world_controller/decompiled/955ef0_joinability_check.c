
undefined8 FUN_00955ef0(undefined8 param_1,long *param_2,uint *param_3,uint param_4)

{
  char cVar1;
  byte bVar2;
  undefined4 uVar3;
  undefined8 uVar4;
  long lVar5;
  long lVar6;
  long *plVar7;
  undefined8 uVar8;
  long lVar9;
  int *piVar10;
  long *plVar11;
  int iVar12;
  ushort uVar13;
  uint uVar14;
  bool bVar15;
  undefined1 local_101;
  char local_d9;
  uint local_d0 [2];
  long local_c8;
  uint local_c0 [2];
  long local_b8;
  undefined1 local_ac [4];
  long local_a8;
  uint local_a0;
  int local_9c;
  undefined8 local_98;
  ushort local_3e;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  local_101 = 0;
  if (((param_2 != (long *)0x0) && (*param_2 != 0)) && (param_3 != (uint *)0x0)) {
    *param_3 = 0;
    uVar4 = FUN_0056b260();
    lVar6 = 0;
    if (*param_2 != 0) {
      uVar3 = FUN_00001df0(uVar4);
      lVar5 = FUN_0056dc00(uVar4,7,uVar3,param_2);
      if ((lVar5 != 0) && (uVar4 = FUN_0056b260(), *(long *)(lVar5 + 8) != 0)) {
        uVar3 = FUN_01009850(uVar4);
        lVar6 = FUN_0056dc00(uVar4,7,uVar3,lVar5 + 8);
      }
    }
    uVar4 = FUN_00582a40();
    plVar7 = (long *)FUN_00580840(uVar4,param_2);
    if (plVar7 != (long *)0x0) {
      uVar4 = FUN_00557c40(&DAT_026bc508);
      local_c8 = FUN_005863c0(uVar4);
      local_101 = 1;
      while (local_98 = 0, local_c8 != 0) {
        local_98 = 0;
        FUN_005864b0(uVar4,&local_c8);
        uVar8 = FUN_00582a40();
        cVar1 = FUN_005805b0(uVar8,&local_c8,param_2);
        uVar13 = 0;
        if (cVar1 != '\0') {
          uVar13 = local_3e & 8;
        }
        local_d9 = *(char *)((long)plVar7 + 0x24);
        lVar5 = FUN_00775180(1);
        if (((*(uint *)(lVar5 + 0x8c48) < 0xb) &&
            ((0x7f0U >> (*(uint *)(lVar5 + 0x8c48) & 0x1f) & 1) != 0)) &&
           (cVar1 = FUN_00b742d0(lVar5), cVar1 != '\0')) {
          lVar9 = FUN_00b74340(lVar5);
          uVar14 = 0;
          lVar5 = lVar9 + 0x1ca0;
          do {
            if (((*(uint *)(&DAT_00001c54 + lVar9) >> (uVar14 & 0x1f) & 1) != 0) &&
               (cVar1 = FUN_002b82d0(lVar5,param_1), cVar1 != '\0')) {
              local_d9 = *(char *)((long)plVar7 + 0x25);
              break;
            }
            lVar5 = lVar5 + 0xe8;
            uVar14 = uVar14 + 1;
          } while ((int)uVar14 < 0x14);
        }
        local_a0 = 0;
        cVar1 = FUN_00b2a6d0(&local_9c,0,0,0,0,0,0,&local_a0,&local_a8);
        iVar12 = 0;
        if (cVar1 != '\0') {
          piVar10 = (int *)(local_a8 + 0xc);
          uVar14 = 0;
          iVar12 = 0;
          do {
            if ((local_a0 >> (uVar14 & 0x1f) & 1) != 0) {
              iVar12 = iVar12 + (uint)(*piVar10 == local_9c);
            }
            piVar10 = piVar10 + 0x3a;
            uVar14 = uVar14 + 1;
          } while (uVar14 != 0x14);
        }
        cVar1 = *(char *)((long)plVar7 + 0x2c);
        local_d0[0] = 0;
        if (*(short *)((long)plVar7 + 10) == -1) {
          if (local_d9 < iVar12) {
            local_d0[0] = 4;
          }
        }
        else if (local_d9 < iVar12) {
          iVar12 = FUN_00264310();
          if (iVar12 == cVar1) {
            local_d0[0] = local_d0[0] | 2;
          }
          else {
            local_d0[0] = local_d0[0] | 1;
          }
        }
        cVar1 = *(char *)((long)plVar7 + 0x26);
        if (cVar1 == '\x03') {
          local_d0[0] = local_d0[0] | 0x10000;
        }
        else if (cVar1 == '\x02') {
          if ((param_4 | 2) != 2) {
            local_d0[0] = local_d0[0] | 0x2000;
          }
        }
        else if (((cVar1 == '\x01') && ((param_4 | 2) != 2)) && (uVar13 == 0)) {
          local_d0[0] = local_d0[0] | 0x1000;
        }
        if (*(short *)((long)plVar7 + 10) != -1) {
          cVar1 = FUN_00547eb0();
          lVar5 = FUN_005753c0(4);
          bVar15 = false;
          if ((short)plVar7[1] != -1) {
            bVar15 = (short)plVar7[1] != *(short *)((long)plVar7 + 10);
          }
          if (lVar5 != 0) {
            if (cVar1 == '\0') {
              FUN_00547920(lVar5,*(undefined2 *)((long)plVar7 + 10),local_d0);
              if (bVar15) {
                FUN_00547920(lVar5,(short)plVar7[1],local_d0);
              }
            }
            else {
              FUN_00547840();
              if (bVar15) {
                FUN_00547840(lVar5,(short)plVar7[1],local_d0);
              }
            }
          }
        }
        if ((lVar6 != 0) &&
           (lVar5 = *(long *)(lVar6 + 0x90), lVar9 = FUN_0078c210(), lVar5 != lVar9)) {
          local_d0[0] = local_d0[0] | 0x40000;
        }
        local_c0[0] = 0;
        cVar1 = FUN_00b2a6d0(0,0,0,0,0,0,local_ac,local_c0,&local_b8);
        if (cVar1 != '\0') {
          plVar11 = (long *)(local_b8 + 0x90);
          uVar14 = 0;
          do {
            if (((local_c0[0] >> (uVar14 & 0x1f) & 1) != 0) && (*plVar11 == *plVar7)) {
              local_d0[0] = local_d0[0] | 0x20000;
            }
            plVar11 = plVar11 + 0x1d;
            uVar14 = uVar14 + 1;
          } while (uVar14 != 0x14);
        }
        cVar1 = FUN_00b21010();
        if (((cVar1 == '\0') && (cVar1 = FUN_00b21030(), cVar1 == '\0')) &&
           (iVar12 = FUN_007850a0(), 0x1b < iVar12)) {
          if (iVar12 < 0x24) {
            local_d0[0] = local_d0[0] | 0x80000;
          }
          else {
            local_d0[0] = local_d0[0] | 0x100000;
          }
        }
        lVar5 = FUN_00574ef0();
        if (*(char *)(lVar5 + 300) != '\0') {
          local_d0[0] = local_d0[0] | 0x8000;
        }
        bVar2 = *(byte *)((long)plVar7 + 0x27);
        if ((bVar2 & 1) != 0) {
          local_d0[0] = local_d0[0] | 8;
          bVar2 = *(byte *)((long)plVar7 + 0x27);
        }
        if ((bVar2 & 2) != 0) {
          local_d0[0] = local_d0[0] | 0x10;
          bVar2 = *(byte *)((long)plVar7 + 0x27);
        }
        if ((bVar2 & 8) != 0) {
          local_d0[0] = local_d0[0] | 0x20;
          bVar2 = *(byte *)((long)plVar7 + 0x27);
        }
        if ((bVar2 & 0x10) != 0) {
          local_d0[0] = local_d0[0] | 0x40;
          bVar2 = *(byte *)((long)plVar7 + 0x27);
        }
        if ((bVar2 & 4) != 0) {
          local_d0[0] = local_d0[0] | 0x4000;
        }
        *param_3 = *param_3 | local_d0[0];
        local_c8 = FUN_00586430(uVar4,&local_c8);
      }
    }
  }
  if (*DAT_01a1f100 == local_38) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),local_101);
  }
  uVar4 = thunk_FUN_012aa7f6();
  return uVar4;
}

