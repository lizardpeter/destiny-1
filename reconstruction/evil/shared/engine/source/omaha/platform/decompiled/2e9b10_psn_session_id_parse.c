
undefined1 FUN_002e9b10(long param_1,short *param_2)

{
  char cVar1;
  char cVar2;
  long lVar3;
  byte bVar4;
  char cVar5;
  short sVar6;
  short sVar7;
  int iVar8;
  char cVar9;
  char cVar10;
  char cVar11;
  short sVar12;
  char cVar13;
  char cVar14;
  char cVar15;
  undefined1 local_31;
  
  lVar3 = thunk_FUN_012aa816();
  local_31 = 0;
  if (0x27 < lVar3) {
    sVar6 = 0;
    lVar3 = 0;
    do {
      cVar13 = *(char *)(param_1 + lVar3);
      bVar4 = cVar13 - 0x30;
      if (9 < bVar4) {
        if ((byte)(cVar13 + 0xbfU) < 6) {
          bVar4 = cVar13 - 0x37;
        }
        else {
          if (5 < (byte)(cVar13 + 0x9fU)) {
            return 0;
          }
          bVar4 = cVar13 + 0xa9;
        }
      }
      sVar6 = (ushort)bVar4 + sVar6 * 0x10;
      lVar3 = lVar3 + 1;
    } while ((int)lVar3 < 3);
    if (*(char *)(param_1 + 3) == '-') {
      iVar8 = 0;
      lVar3 = 0;
      do {
        cVar13 = *(char *)(param_1 + 4 + lVar3);
        bVar4 = cVar13 - 0x30;
        if (9 < bVar4) {
          if ((byte)(cVar13 + 0xbfU) < 6) {
            bVar4 = cVar13 - 0x37;
          }
          else {
            if (5 < (byte)(cVar13 + 0x9fU)) {
              return 0;
            }
            bVar4 = cVar13 + 0xa9;
          }
        }
        iVar8 = (uint)bVar4 + iVar8 * 0x10;
        lVar3 = lVar3 + 1;
      } while ((int)lVar3 < 8);
      if (*(char *)(param_1 + 0xc) == '-') {
        sVar7 = 0;
        lVar3 = 0;
        do {
          cVar13 = *(char *)(param_1 + 0xd + lVar3);
          bVar4 = cVar13 - 0x30;
          if (9 < bVar4) {
            if ((byte)(cVar13 + 0xbfU) < 6) {
              bVar4 = cVar13 - 0x37;
            }
            else {
              if (5 < (byte)(cVar13 + 0x9fU)) {
                return 0;
              }
              bVar4 = cVar13 + 0xa9;
            }
          }
          sVar7 = (ushort)bVar4 + sVar7 * 0x10;
          lVar3 = lVar3 + 1;
        } while ((int)lVar3 < 4);
        if (*(char *)(param_1 + 0x11) == '-') {
          sVar12 = 0;
          lVar3 = 0;
          do {
            cVar13 = *(char *)(param_1 + 0x12 + lVar3);
            bVar4 = cVar13 - 0x30;
            if (9 < bVar4) {
              if ((byte)(cVar13 + 0xbfU) < 6) {
                bVar4 = cVar13 - 0x37;
              }
              else {
                if (5 < (byte)(cVar13 + 0x9fU)) {
                  return 0;
                }
                bVar4 = cVar13 + 0xa9;
              }
            }
            sVar12 = (ushort)bVar4 + sVar12 * 0x10;
            lVar3 = lVar3 + 1;
          } while ((int)lVar3 < 4);
          if (*(char *)(param_1 + 0x16) == '-') {
            cVar13 = '\0';
            lVar3 = 0;
            do {
              cVar14 = *(char *)(param_1 + 0x17 + lVar3);
              bVar4 = cVar14 - 0x30;
              if (9 < bVar4) {
                if ((byte)(cVar14 + 0xbfU) < 6) {
                  bVar4 = cVar14 - 0x37;
                }
                else {
                  if (5 < (byte)(cVar14 + 0x9fU)) {
                    return 0;
                  }
                  bVar4 = cVar14 + 0xa9;
                }
              }
              cVar13 = bVar4 + cVar13 * '\x10';
              lVar3 = lVar3 + 1;
            } while ((int)lVar3 < 2);
            cVar14 = '\0';
            lVar3 = 0;
            do {
              cVar9 = *(char *)(param_1 + 0x19 + lVar3);
              bVar4 = cVar9 - 0x30;
              if (9 < bVar4) {
                if ((byte)(cVar9 + 0xbfU) < 6) {
                  bVar4 = cVar9 - 0x37;
                }
                else {
                  if (5 < (byte)(cVar9 + 0x9fU)) {
                    return 0;
                  }
                  bVar4 = cVar9 + 0xa9;
                }
              }
              cVar14 = bVar4 + cVar14 * '\x10';
              lVar3 = lVar3 + 1;
            } while ((int)lVar3 < 2);
            if (*(char *)(param_1 + 0x1b) == '-') {
              cVar9 = '\0';
              lVar3 = 0;
              do {
                cVar10 = *(char *)(param_1 + 0x1c + lVar3);
                bVar4 = cVar10 - 0x30;
                if (9 < bVar4) {
                  if ((byte)(cVar10 + 0xbfU) < 6) {
                    bVar4 = cVar10 - 0x37;
                  }
                  else {
                    if (5 < (byte)(cVar10 + 0x9fU)) {
                      return 0;
                    }
                    bVar4 = cVar10 + 0xa9;
                  }
                }
                cVar9 = bVar4 + cVar9 * '\x10';
                lVar3 = lVar3 + 1;
              } while ((int)lVar3 < 2);
              cVar10 = '\0';
              lVar3 = 0;
              do {
                cVar11 = *(char *)(param_1 + 0x1e + lVar3);
                bVar4 = cVar11 - 0x30;
                if (9 < bVar4) {
                  if ((byte)(cVar11 + 0xbfU) < 6) {
                    bVar4 = cVar11 - 0x37;
                  }
                  else {
                    if (5 < (byte)(cVar11 + 0x9fU)) {
                      return 0;
                    }
                    bVar4 = cVar11 + 0xa9;
                  }
                }
                cVar10 = bVar4 + cVar10 * '\x10';
                lVar3 = lVar3 + 1;
              } while ((int)lVar3 < 2);
              cVar11 = '\0';
              lVar3 = 0;
              do {
                cVar15 = *(char *)(param_1 + 0x20 + lVar3);
                bVar4 = cVar15 - 0x30;
                if (9 < bVar4) {
                  if ((byte)(cVar15 + 0xbfU) < 6) {
                    bVar4 = cVar15 - 0x37;
                  }
                  else {
                    if (5 < (byte)(cVar15 + 0x9fU)) {
                      return 0;
                    }
                    bVar4 = cVar15 + 0xa9;
                  }
                }
                cVar11 = bVar4 + cVar11 * '\x10';
                lVar3 = lVar3 + 1;
              } while ((int)lVar3 < 2);
              cVar15 = '\0';
              lVar3 = 0;
              do {
                cVar5 = *(char *)(param_1 + 0x22 + lVar3);
                bVar4 = cVar5 - 0x30;
                if (9 < bVar4) {
                  if ((byte)(cVar5 + 0xbfU) < 6) {
                    bVar4 = cVar5 - 0x37;
                  }
                  else {
                    if (5 < (byte)(cVar5 + 0x9fU)) {
                      return 0;
                    }
                    bVar4 = cVar5 + 0xa9;
                  }
                }
                cVar15 = bVar4 + cVar15 * '\x10';
                lVar3 = lVar3 + 1;
              } while ((int)lVar3 < 2);
              cVar5 = '\0';
              lVar3 = 0;
              do {
                cVar2 = *(char *)(param_1 + 0x24 + lVar3);
                bVar4 = cVar2 - 0x30;
                if (9 < bVar4) {
                  if ((byte)(cVar2 + 0xbfU) < 6) {
                    bVar4 = cVar2 - 0x37;
                  }
                  else {
                    if (5 < (byte)(cVar2 + 0x9fU)) {
                      return 0;
                    }
                    bVar4 = cVar2 + 0xa9;
                  }
                }
                cVar5 = bVar4 + cVar5 * '\x10';
                lVar3 = lVar3 + 1;
              } while ((int)lVar3 < 2);
              cVar2 = '\0';
              lVar3 = 0;
              do {
                cVar1 = *(char *)(param_1 + 0x26 + lVar3);
                bVar4 = cVar1 - 0x30;
                if (9 < bVar4) {
                  if ((byte)(cVar1 + 0xbfU) < 6) {
                    bVar4 = cVar1 - 0x37;
                  }
                  else {
                    if (5 < (byte)(cVar1 + 0x9fU)) {
                      return 0;
                    }
                    bVar4 = cVar1 + 0xa9;
                  }
                }
                cVar2 = bVar4 + cVar2 * '\x10';
                lVar3 = lVar3 + 1;
              } while ((int)lVar3 < 2);
              *param_2 = sVar6;
              *(int *)(param_2 + 1) = iVar8;
              param_2[3] = sVar7;
              param_2[4] = sVar12;
              *(char *)(param_2 + 5) = cVar13;
              *(char *)((long)param_2 + 0xb) = cVar14;
              local_31 = 1;
              *(char *)(param_2 + 6) = cVar9;
              *(char *)((long)param_2 + 0xd) = cVar10;
              *(char *)(param_2 + 7) = cVar11;
              *(char *)((long)param_2 + 0xf) = cVar15;
              *(char *)(param_2 + 8) = cVar5;
              *(char *)((long)param_2 + 0x11) = cVar2;
            }
          }
        }
      }
    }
  }
  return local_31;
}

