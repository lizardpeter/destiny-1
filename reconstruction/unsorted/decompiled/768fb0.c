
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00768fb0(int *param_1)

{
  int *piVar1;
  uint uVar2;
  byte bVar3;
  char cVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  long lVar8;
  long *plVar9;
  long lVar10;
  long lVar11;
  undefined8 uVar12;
  long lVar13;
  byte bVar14;
  undefined4 uVar15;
  undefined1 local_178 [320];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  if ((char)param_1[2] == '\0') {
    lVar8 = FUN_00775180(param_1[1]);
  }
  else {
    lVar8 = FUN_00772ec0();
  }
  iVar5 = *param_1;
  if (iVar5 == 0) {
    bVar14 = *(byte *)(param_1 + 8);
    if ((bVar14 & 3) == 3) {
      uVar2 = *(uint *)(lVar8 + 0x8c48);
      if ((((uVar2 & 0xfffffffe) != 6) && (uVar2 != 8)) && (uVar2 != 9)) {
        iVar5 = FUN_0076a010(param_1);
        if (iVar5 != 0) {
          FUN_00768bc0(param_1);
          lVar8 = thunk_FUN_00768060();
          if (lVar8 != 0) {
            FUN_0076e5a0(lVar8);
          }
          cVar4 = FUN_000e4d70(6,1);
          if (cVar4 != '\0') {
            if ((DAT_026ca240 == '\0') && (iVar5 = thunk_FUN_012aa7d6(&DAT_026ca240), iVar5 != 0)) {
              DAT_026ca238 = FUN_000e4a10(s_world_controller_matchmaking_man_0164d220);
              thunk_FUN_012aa7e6(&DAT_026ca240);
            }
            FUN_01008290(local_178,s_world_controller_matchmaking_man_0164d220);
            FUN_000e4aa0(DAT_026ca238,local_178);
          }
        }
        goto LAB_00769829;
      }
      plVar9 = (long *)FUN_005979c0();
      lVar10 = (**(code **)(*plVar9 + 0x60))(plVar9,*param_1);
      lVar11 = FUN_00b74340(lVar8);
      iVar5 = FUN_00b82620(lVar11);
      iVar6 = 0;
      while (iVar5 != -1) {
        iVar6 = iVar6 + (uint)(*(int *)(lVar11 + 0x5c +
                                       (long)*(int *)(&DAT_00001c64 + (long)iVar5 * 0xe8 + lVar11) *
                                       0x168) == 10);
        iVar5 = FUN_00b82650(lVar11);
      }
      if (param_1[5] == 0) {
        lVar8 = FUN_00b74340(lVar8);
        uVar15 = *(undefined4 *)(&DAT_00001c50 + lVar8);
        uVar12 = thunk_FUN_00768060();
        iVar5 = FUN_0076ad90(param_1,uVar15,*(undefined4 *)(lVar10 + 0x9c));
        param_1[5] = iVar5;
        FUN_0076dbd0(uVar12,iVar5);
        cVar4 = FUN_000e4d70(6,2);
        if (cVar4 != '\0') {
          if ((DAT_026ca250 == '\0') && (iVar5 = thunk_FUN_012aa7d6(&DAT_026ca250), iVar5 != 0)) {
            DAT_026ca248 = FUN_000e4a10(s_world_controller_matchmaking_man_0164d271);
            thunk_FUN_012aa7e6(&DAT_026ca250);
          }
          FUN_01008290(local_178,s_world_controller_matchmaking_man_0164d271,param_1[5]);
          FUN_000e4aa0(DAT_026ca248,local_178);
        }
        *(undefined1 *)((long)param_1 + 0x21) = 0;
        if (param_1[5] == 1) {
          *(undefined1 *)((long)param_1 + 0x21) = 1;
        }
        else if (param_1[5] == 2) {
          *(undefined1 *)((long)param_1 + 0x21) = 2;
        }
      }
      iVar5 = param_1[0x806];
      if (iVar5 == -1) {
        param_1[0x806] = iVar6;
        lVar8 = DAT_026553b0;
        iVar5 = iVar6;
        if (DAT_026553a8 == '\0') {
          lVar8 = FUN_000694d0();
          iVar5 = param_1[0x806];
        }
        *(long *)(param_1 + 0x808) = lVar8;
      }
      if (iVar5 < iVar6) {
        lVar8 = DAT_026553b0;
        if (DAT_026553a8 == '\0') {
          lVar8 = FUN_000694d0();
        }
        *(long *)(param_1 + 0x808) = lVar8;
        bVar14 = *(byte *)((long)param_1 + 0x21);
        bVar3 = 0;
        if ((bVar14 & 3) == 3) {
          cVar4 = FUN_000e4d70(6,2);
          if (cVar4 != '\0') {
            if ((DAT_026ca260 == '\0') && (iVar5 = thunk_FUN_012aa7d6(&DAT_026ca260), iVar5 != 0)) {
              DAT_026ca258 = FUN_000e4a10(s_world_controller_matchmaking_man_0164d2b6);
              thunk_FUN_012aa7e6(&DAT_026ca260);
            }
            param_1[0x806] = iVar6;
            FUN_01008290(local_178,s_world_controller_matchmaking_man_0164d2b6,iVar6,iVar6);
            FUN_000e4aa0(DAT_026ca258,local_178);
          }
          bVar14 = *(byte *)((long)param_1 + 0x21) & 0xfe;
          *(byte *)((long)param_1 + 0x21) = bVar14;
          bVar3 = 1;
        }
      }
      else {
        bVar14 = *(byte *)((long)param_1 + 0x21);
        bVar3 = 0;
      }
      param_1[0x806] = iVar6;
      if ((bVar14 & 3) == 1) {
        piVar1 = param_1 + 10;
        cVar4 = FUN_00b2bda0(piVar1);
        if (cVar4 != '\0') {
          iVar5 = FUN_00b403e0();
          plVar9 = (long *)FUN_005979c0();
          lVar8 = (**(code **)(*plVar9 + 0x60))(plVar9,*param_1);
          if ((iVar5 != 3) && (*(char *)(lVar8 + 100) == '\0')) {
            lVar11 = thunk_FUN_00078280(piVar1);
            lVar8 = DAT_026553b0;
            if (DAT_026553a8 == '\0') {
              lVar8 = FUN_000694d0();
            }
            lVar8 = lVar8 - lVar11;
            iVar5 = *(int *)(lVar10 + 0x5c);
            cVar4 = FUN_00b2bdd0(piVar1);
            if (cVar4 == '\0') {
LAB_007694e7:
              if (lVar8 < iVar5 * 1000) goto LAB_007695ea;
              cVar4 = FUN_000e4d70(6,2);
              if (cVar4 != '\0') {
                if ((DAT_026ca280 == '\0') &&
                   (iVar5 = thunk_FUN_012aa7d6(&DAT_026ca280), iVar5 != 0)) {
                  DAT_026ca278 = FUN_000e4a10(s_world_controller_matchmaking_man_0164d3a8);
                  thunk_FUN_012aa7e6(&DAT_026ca280);
                }
                FUN_01008290(local_178,s_world_controller_matchmaking_man_0164d3a8,lVar8);
                uVar15 = DAT_026ca278;
                goto LAB_0076956c;
              }
            }
            else {
              iVar6 = *(int *)(lVar10 + 0x60);
              lVar11 = FUN_00b2bde0(piVar1);
              lVar10 = DAT_026553b0;
              if (DAT_026553a8 == '\0') {
                lVar10 = FUN_000694d0();
              }
              if (lVar10 - lVar11 <= (long)(iVar6 * 1000)) goto LAB_007694e7;
              cVar4 = FUN_000e4d70(6,2);
              if (cVar4 != '\0') {
                if ((DAT_026ca270 == '\0') &&
                   (iVar5 = thunk_FUN_012aa7d6(&DAT_026ca270), iVar5 != 0)) {
                  DAT_026ca268 = FUN_000e4a10(s_world_controller_matchmaking_man_0164d31a);
                  thunk_FUN_012aa7e6(&DAT_026ca270);
                }
                FUN_01008290(local_178,s_world_controller_matchmaking_man_0164d31a,lVar10 - lVar11);
                uVar15 = DAT_026ca268;
LAB_0076956c:
                FUN_000e4aa0(uVar15,local_178);
              }
            }
            cVar4 = FUN_000e4d70(6,2);
            if (cVar4 != '\0') {
              if ((DAT_026ca290 == '\0') && (iVar5 = thunk_FUN_012aa7d6(&DAT_026ca290), iVar5 != 0))
              {
                DAT_026ca288 = FUN_000e4a10(s_world_controller_matchmaking_man_0164d420);
                thunk_FUN_012aa7e6(&DAT_026ca290);
              }
              FUN_01008290(local_178,s_world_controller_matchmaking_man_0164d420,lVar8);
              FUN_000e4aa0(DAT_026ca288,local_178);
            }
            *(byte *)((long)param_1 + 0x21) = *(byte *)((long)param_1 + 0x21) | 2;
          }
        }
      }
LAB_007695ea:
      if (((*(byte *)((long)param_1 + 0x21) & 2) != 0) &&
         ((bool)((*(byte *)((long)param_1 + 0x21) & 1) == 0 & (bVar3 ^ 1)))) {
        lVar8 = *(long *)(param_1 + 6);
        lVar10 = DAT_026553b0;
        if (DAT_026553a8 == '\0') {
          lVar10 = FUN_000694d0();
        }
        iVar5 = FUN_00768460();
        lVar11 = *(long *)(param_1 + 0x808);
        lVar13 = DAT_026553b0;
        if (DAT_026553a8 == '\0') {
          lVar13 = FUN_000694d0();
        }
        iVar6 = FUN_007689a0();
        if (((long)iVar5 < lVar10 - lVar8) &&
           (iVar7 = FUN_000697a0(), 5000 < (uint)(iVar7 - _DAT_026ca298))) {
          cVar4 = FUN_000e4d70(6,1);
          if (cVar4 != '\0') {
            if ((DAT_026ca2a0 == '\0') && (iVar7 = thunk_FUN_012aa7d6(&DAT_026ca2a0), iVar7 != 0)) {
              DAT_026ca29c = FUN_000e4a10(s_world_controller_matchmaking_man_0164d45f);
              thunk_FUN_012aa7e6(&DAT_026ca2a0);
            }
            FUN_01008290(local_178,s_world_controller_matchmaking_man_0164d45f);
            FUN_000e4aa0(DAT_026ca29c,local_178);
          }
          _DAT_026ca298 = FUN_000697a0();
        }
        if ((long)iVar6 < lVar13 - lVar11) {
          iVar6 = FUN_000697a0();
          if (5000 < (uint)(iVar6 - _DAT_026ca2a8)) {
            cVar4 = FUN_000e4d70(6,1);
            if (cVar4 != '\0') {
              if ((DAT_026ca2b0 == '\0') && (iVar6 = thunk_FUN_012aa7d6(&DAT_026ca2b0), iVar6 != 0))
              {
                DAT_026ca2ac = FUN_000e4a10(s_world_controller_matchmaking_man_0164d4b9);
                thunk_FUN_012aa7e6(&DAT_026ca2b0);
              }
              FUN_01008290(local_178,s_world_controller_matchmaking_man_0164d4b9);
              FUN_000e4aa0(DAT_026ca2ac,local_178);
            }
            _DAT_026ca2a8 = FUN_000697a0();
          }
          if ((long)iVar5 < lVar10 - lVar8) {
            cVar4 = FUN_000e4d70(6,1);
            if (cVar4 != '\0') {
              if ((DAT_026ca2c0 == '\0') && (iVar5 = thunk_FUN_012aa7d6(&DAT_026ca2c0), iVar5 != 0))
              {
                DAT_026ca2b8 = FUN_000e4a10(s_world_controller_matchmaking_man_0164d524);
                thunk_FUN_012aa7e6(&DAT_026ca2c0);
              }
              FUN_01008290(local_178,s_world_controller_matchmaking_man_0164d524);
              FUN_000e4aa0(DAT_026ca2b8,local_178);
            }
            *(byte *)((long)param_1 + 0x21) = *(byte *)((long)param_1 + 0x21) | 1;
          }
        }
      }
      goto LAB_00769829;
    }
    if ((bVar14 & 2) != 0) goto LAB_007691a6;
    if ((bVar14 & 1) != 0) goto LAB_00769829;
  }
  else if (iVar5 == 1) {
    if ((*(byte *)(param_1 + 8) & 2) != 0) {
LAB_007691a6:
      FUN_0076b060(param_1);
      goto LAB_00769829;
    }
  }
  else {
    if (iVar5 != 2) goto LAB_00769829;
    if ((*(byte *)(param_1 + 8) & 1) != 0) {
      cVar4 = FUN_00b2bdc0(param_1 + 10);
      bVar14 = *(byte *)((long)param_1 + 0x21);
      if (cVar4 != '\0') {
        bVar14 = bVar14 & 0xfe;
        *(byte *)((long)param_1 + 0x21) = bVar14;
      }
      *(byte *)((long)param_1 + 0x21) = bVar14 & 0xfd;
      goto LAB_00769829;
    }
  }
  if ((*(byte *)((long)param_1 + 0x21) & 7) != 0) {
    FUN_00768bc0(param_1);
  }
LAB_00769829:
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

