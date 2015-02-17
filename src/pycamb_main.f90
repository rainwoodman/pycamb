module pycamb_mod 
    use pycamb_parameters
    use errors
    double precision, dimension(:,:,:), allocatable :: transfers
    double precision, dimension(:), allocatable :: transfers_k,transfers_sigma8
    real, dimension(:,:,:), allocatable :: matter_power
    double precision, dimension(:,:), allocatable :: matter_power_kh
    double precision :: output_cl_scale=7.4311e12
    contains
    
    subroutine getcls(paramVec,lmax,Max_eta_k,cls)
        use camb
        implicit none
        real, intent(in) :: paramVec(1024)
        integer, intent(in) :: lmax, Max_eta_k
        real, intent(out) ::  cls(2:lmax,4)
        type(CAMBparams) :: P
        call CAMB_SetDefParams(P)
        call makeParameters(paramVec,P)
        P%max_l=lmax
        P%Max_l_tensor=lmax
        P%Max_eta_k=Max_eta_k
        P%Max_eta_k_tensor=Max_eta_k
        call CAMB_GetResults(P)
        if (global_error_flag /= 0) return
        call CAMB_GetCls(cls, lmax, 1, .false.)
        cls=cls*output_cl_scale
    end subroutine getcls
    
    
    subroutine getage(paramVec,age)
        use camb
        implicit none
        real, intent(in) :: paramVec(1024)
        double precision, intent(out) ::  age
        type(CAMBparams) :: P
        call CAMB_SetDefParams(P)
        call makeParameters(paramVec,P)
        age = CAMB_GetAge(P)
    end subroutine getage

    subroutine gentransfers(paramVec,lmax,nred,redshifts)
        use camb
        implicit none
        real, intent(in) :: paramVec(1024)
        integer, intent(in) :: nred, lmax
        double precision, intent(in), dimension(nred) :: redshifts
        type(CAMBparams) :: P
        integer :: nr, i
        nr = size(redshifts)
        call CAMB_SetDefParams(P)
        call makeParameters(paramVec,P)
        P%WantTransfer = .true.
        P%max_l=lmax
        P%Max_l_tensor=lmax
        P%Max_eta_k=2*lmax
        P%Max_eta_k_tensor=2*lmax
        P%transfer%num_redshifts = nr
        P%transfer%PK_num_redshifts = nr
        do i=1,nr
            P%transfer%redshifts(i)=redshifts(i)
            P%transfer%PK_redshifts(i)=redshifts(i)
            P%transfer%PK_redshifts_index(i)=i
        enddo
        call CAMB_GetResults(P)
        if (global_error_flag /= 0) return
        allocate(transfers(Transfer_max,MT%num_q_trans,nred))
        allocate(transfers_k(MT%num_q_trans))
        allocate(transfers_sigma8(nred))
        transfers = MT%TransferData
        transfers_k = MT%q_trans
        transfers_sigma8 = MT%sigma_8(:,1)
    end subroutine gentransfers

    subroutine freetransfers()
        deallocate(transfers)
        deallocate(transfers_k)
        deallocate(transfers_sigma8)
    end subroutine freetransfers

    subroutine freematterpower()
    deallocate(matter_power)
    deallocate(matter_power_kh)
    end subroutine freematterpower

subroutine genpowerandcls(paramVec,lmax,dlogk,maxk,Max_eta_k,nred,redshifts,cls)
            use camb
            implicit none
            real, intent(out) ::  cls(2:lmax,4)
            real, intent(in) :: paramVec(1024)
            integer, intent(in) :: nred, lmax, Max_eta_k
            real, intent(in) ::  maxk, dlogk
            real, parameter :: minkh = 1.0e-4
            double precision, intent(in), dimension(nred) :: redshifts
            type(CAMBparams) :: P
            integer :: nr, i
            integer in,itf, points, points_check
            nr = size(redshifts)
            call CAMB_SetDefParams(P)
            call makeParameters(paramVec,P)
            P%WantTransfer = .true.
            P%max_l=lmax
            P%Max_l_tensor=lmax
            P%Max_eta_k=Max_eta_k
            P%Max_eta_k_tensor=Max_eta_k
            P%transfer%num_redshifts = nr
            P%transfer%PK_num_redshifts = nr
            do i=1,nr
                P%transfer%redshifts(i)=redshifts(i)
                P%transfer%PK_redshifts(i)=redshifts(i)
                P%transfer%PK_redshifts_index(i)=i
            enddo
            call CAMB_GetResults(P)
            if (global_error_flag /= 0) return
            call CAMB_GetCls(cls, lmax, 1, .false.)
            if (global_error_flag /= 0) return
            cls=cls*output_cl_scale
            itf=1
            P%transfer%num_redshifts = nr
            P%transfer%kmax = maxk * (P%h0/100._dl)
            P%transfer%k_per_logint = dlogk
    
             points = log(MT%TransferData(Transfer_kh,MT%num_q_trans,itf)/minkh)/dlogk+1
            allocate(matter_power(points,CP%InitPower%nn,nr))
            allocate(matter_power_kh(points,nr))

            do itf=1, CP%Transfer%num_redshifts
                points_check = log(MT%TransferData(Transfer_kh,MT%num_q_trans,itf)/minkh)/dlogk+1
                 if (points_check .ne. points)  stop 'Problem with pycamb assumption on k with z'
                 do in = 1, CP%InitPower%nn
                  call Transfer_GetMatterPower(MT,matter_power(:,in,itf), itf, in, minkh,dlogk, points)
                 end do
                 do i=1,points
                  matter_power_kh(i,itf)=minkh*exp((i-1)*dlogk)
                 end do
            enddo !End redshifts loop
    
        end subroutine genpowerandcls

!        subroutine freetransfers()
!            deallocate(transfers)
!            deallocate(transfers_k)
!            deallocate(transfers_sigma8)
!        end subroutine freetransfers

    
    subroutine getpower(paramVec,maxk,dlogk,nred,redshifts)
        use camb
        implicit none
        real, intent(in) :: paramVec(1024)
        integer, intent(in) :: nred
        integer :: lmax
        double precision, intent(in), dimension(nred) :: redshifts
        type(CAMBparams) :: P
        integer :: nr, i
        real, intent(in) ::  maxk, dlogk
        real, parameter :: minkh = 1.0e-4
        integer in,itf, points, points_check
        nr = size(redshifts)
        call CAMB_SetDefParams(P)
        call makeParameters(paramVec,P)
        P%WantTransfer = .true.
        lmax=10000
        P%max_l=lmax
        P%Max_l_tensor=lmax
        P%Max_eta_k=2*lmax
        P%Max_eta_k_tensor=2*lmax
        P%transfer%num_redshifts = nr
        
        P%transfer%kmax = maxk * (P%h0/100._dl)
        P%transfer%k_per_logint = dlogk

        P%transfer%PK_num_redshifts = nr
        do i=1,nr
            P%transfer%redshifts(i)=redshifts(i)
            P%transfer%PK_redshifts(i)=redshifts(i)
            P%transfer%PK_redshifts_index(i)=i
        enddo
        call CAMB_GetResults(P)
        if (global_error_flag /= 0) return

        itf=1
         points = log(MT%TransferData(Transfer_kh,MT%num_q_trans,itf)/minkh)/dlogk+1
        allocate(matter_power(points,CP%InitPower%nn,nr))
        allocate(matter_power_kh(points,nr))
        
        do itf=1, CP%Transfer%num_redshifts
            points_check = log(MT%TransferData(Transfer_kh,MT%num_q_trans,itf)/minkh)/dlogk+1
             if (points_check .ne. points)  stop 'Problem with pycamb assumption on k with z'
             do in = 1, CP%InitPower%nn
              call Transfer_GetMatterPower(MT,matter_power(:,in,itf), itf, in, minkh,dlogk, points)
!              if (CP%OutputNormalization == outCOBE) then
!                 if (allocated(COBE_scales)) then
!                  outpower(:,in) = outpower(:,in)*COBE_scales(in)
!                 else
!                  if (FeedbackLevel>0) write (*,*) 'Cannot COBE normalize - no Cls generated'
!                 end if
!             end if
             end do
             do i=1,points
              matter_power_kh(i,itf)=minkh*exp((i-1)*dlogk)
             end do
        enddo !End redshifts loop
    end subroutine getpower

    subroutine freepower()
        deallocate(matter_power)
        deallocate(matter_power_kh)
    end subroutine freepower

    function angularDiameter(paramVec,z)
        use ModelParams, only : CAMBparams, camb_angulardiameter => AngularDiameterDistance
        use camb, only : CAMB_SetDefParams, CAMBParams_Set
        implicit none
        double precision, intent(in) :: z
        double precision :: angularDiameter
        real, intent(in) :: paramVec(1024)
        integer error
        type(CAMBparams) :: P        
        call CAMB_SetDefParams(P)
        call makeParameters(paramVec,P)
        call CAMBParams_Set(P,error)
        angularDiameter = camb_angulardiameter(z)
    end function angularDiameter

    subroutine angularDiameterVector(paramVec,n,z,ang)
        !Should be in temporal order ie redshift decreasing
        use ModelParams, only : CAMBparams, DeltaTime, rofchi
        use camb, only : CAMB_SetDefParams, CAMBParams_Set, CP
        implicit none
        integer, intent(in) :: n
        integer :: nz
        double precision,dimension(n), intent(in) :: z
        double precision,dimension(n), intent(out) :: ang
        real, intent(in) :: paramVec(1024)
        integer error
        integer i,j
        type(CAMBparams) :: P        
        nz=size(z)
        call CAMB_SetDefParams(P)
        call makeParameters(paramVec,P)
        call CAMBParams_Set(P,error)
        ang(nz) = rofchi(DeltaTime(1/(1+z(nz)),1.0_8)/CP%r)
        do i=1,nz-1
            j=nz-i
            ang(j) = rofchi(DeltaTime(1.0/(1.0+z(j)),1./(1.+z(j+1)))/CP%r) + ang(j+1)
        enddo
        ang = ang * CP%r/(1+z)
    end subroutine angularDiameterVector

    
    subroutine setCLTemplatePath(path)
        use camb
        implicit none
        character(LEN=1024), intent(in) :: path
        highL_unlensed_cl_template = path
    end subroutine setCLTemplatePath

end module pycamb_mod
