module DaliLiteModule
  implicit none
  include 'parsizes.for'

  ! Define all shared variables
  integer, parameter :: maxlinks = 100000
  integer, parameter :: maxocc = 60000

  ! Shared arrays
  real, allocatable :: midpoint(:,:), direction(:,:), neidist(:,:)
  integer, allocatable :: segmentrange(:,:)
  character, allocatable :: secstr(:)

  ! Box and linking data
  integer, allocatable :: box(:,:,:), link_a(:), link_b(:), link_c(:)
  real, allocatable :: link_from(:,:), link_to(:,:)
  integer, allocatable :: link_next(:)
  integer :: lastlink

  ! Occupancy tracking
  integer, allocatable :: occ(:,:)
  integer :: nocc

contains

  subroutine preparex(x, iseg, jseg, nx)
    implicit none
    integer, intent(in) :: iseg, jseg, nx
    real, intent(out) :: x(3, 3 + 2 * nx)
    integer :: i, kseg

    do i = 1, 3
      x(i, 1) = midpoint(i, iseg)
      x(i, 2) = midpoint(i, iseg) + direction(i, iseg)
      x(i, 3) = midpoint(i, jseg)
    end do

    do kseg = 1, nx
      do i = 1, 3
        x(i, 3 + kseg) = midpoint(i, kseg) - direction(i, kseg)
        x(i, 3 + nx + kseg) = midpoint(i, kseg) + direction(i, kseg)
      end do
    end do
  end subroutine preparex

  subroutine compare(nseg, rcut, bestpair, protcount)
    implicit none
    integer, intent(in) :: nseg
    real, intent(in) :: rcut
    integer, intent(out) :: bestpair(4), protcount

    integer :: iseg, jseg, kseg, i, count(maxseg, maxseg), protein_nseg
    real :: x(3, 3 + 2 * maxseg), midx(3), dirx(3), distance

    protcount = 0
    bestpair = 0

    do iseg = 1, nseg
      do jseg = 1, nseg
        if (iseg /= jseg .and. neidist(iseg, jseg) < rcut) then
          call initcomparison(protein_nseg, count)
          call preparex(x, iseg, jseg, nseg)
          call twist(x, 3 + 2 * nseg)

          ! Comparison logic
          do kseg = 1, nseg
            if (kseg /= iseg) then
              do i = 1, 3
                midx(i) = (x(i, 3 + kseg) + x(i, 3 + nseg + kseg)) / 2
                dirx(i) = x(i, 3 + nseg + kseg) - midx(i)
              end do

              ! Perform checks
              if (distance(midx, x(:, 3 + kseg)) < 4.0) then
                count(iseg, jseg) = count(iseg, jseg) + 1
              end if
            end if
          end do
        end if
      end do
    end do
  end subroutine compare

  subroutine initcomparison(protein_nseg, count)
    implicit none
    integer, intent(in) :: protein_nseg
    integer, intent(out) :: count(maxseg, maxseg)
    integer :: j, k

    count = 0
  end subroutine initcomparison

  function distance(a, b) result(d)
    real, intent(in) :: a(3), b(3)
    real :: d

    d = sqrt(sum((a - b) ** 2))
  end function distance

end module DaliLiteModule
