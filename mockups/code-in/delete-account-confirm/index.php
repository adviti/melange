<?php include '../includes/header.php'?>

    <div class="grid_3 side">
        <div class="block block-main-nav">
            <ul class="menu">
                <li><a href="javascript:void(0)">My Dashboard</a>
                    <ul>
                        <li class="active"><a href="javascript:void(0)">Create a new task</a></li>
                    </ul>
                </li>
                <li><a href="javascript:void(0)">About Us</a></li>
                <li><a href="javascript:void(0)">Get Started</a></li>
                <li><a href="javascript:void(0)">Participating Organizations</a></li>
                <li><a href="javascript:void(0)">Blog</a></li>
            </ul>
        </div>
        <!-- end .block.block-main-nav -->
        
        <div class="block block-status block-status-sm">
            <div class="block-status-user">
                You are logged in as: <a href="javascript:void(0)">eric_schmidt@gmail.com</a> <a href="javascript:void(0)">(change)</a>
            </div>
            <div class="block-status-action block-status-action-single clearfix">
                <a href="javascript:void(0)" class="block-status-action-dashboard"><span>My Dashboard</span></a>
            </div>
        </div>
        <!-- end .block.block-status.block-status-sm -->
    </div>
    <!-- end .grid_3.side -->
    <div class="grid_9 main">
		<div class="block block-page block-delete-account">
			<div class="block-form-title">
			    <span class="title">Delete your account?</span>
			</div>
			<div class="block-content clearfix">
				<p>Once your account is deleted, all your information will be gone forever.</p>
				<p>Una vez que su cuenta se elimina toda la información se ha ido para siempre.</p>
				<p>Une fois que votre compte est supprimé, toutes vos informations auront disparu pour toujours.</p>
				<form action="#" method="post" class="clearfix">
				<p class="delete-btn-p"><input value="Delete Account" class="delete-btn" type="button" /></p>
				</form>
			</div>
		</div>
    </div>
    <!-- end .grid_9.main -->

<?php include '../includes/footer.php'?>