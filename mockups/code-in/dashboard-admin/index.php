<?php include '../includes/header.php'?>

    <div class="grid_3 side">
        <div class="block block-main-nav">
            <ul class="menu">
                <li class="active"><a href="javascript:void(0)">My Dashboard</a></li>
                <li><a href="javascript:void(0)">About Us</a></li>
                <li><a href="javascript:void(0)">Get Started</a></li>
                <li><a href="javascript:void(0)">Participating Organizations</a></li>
                <li><a href="javascript:void(0)">Blog</a></li>
            </ul>
        </div>
        <!-- end .block.block-main-nav -->
        
        <div class="block block-status block-status-sm">
            <div class="block-status-user">
                You are logged in as: <a href="javascript:void(0)">carol.smith@gmail.com</a> <a href="javascript:void(0)">(change)</a>
            </div>
            <div class="block-status-action block-status-action-single clearfix">
                <a href="javascript:void(0)" class="block-status-action-dashboard"><span>My Dashboard</span></a>
            </div>
        </div>
        <!-- end .block.block-status.block-status-sm -->
    </div>
    <!-- end .grid_3.side -->
    <div class="grid_9 main">
        <div class="block block-user-welcome clearfix">
            <div class="block-user-welcome-title">
                <span class="subhead">Organization admin name</span>
                <span class="name">Carol Smith</span>
            </div>
            <form action="#" method="post">
            	<input type="submit" class="btn" value="Create a task" />
            </form>
        </div>
        <!-- end .block.block-user-welcome -->
        <div class="block block-tabs block-user-tabs">
            <ul>
            	<li><a href="#active-tasks">Active tasks</a></li>
            	<li><a href="#all-tasks">All tasks</a></li>
            </ul>
            <div id="active-tasks" class="task-group">
            	<div class="block-filter clearfix">
            		<div class="block-filter-option block-filter-option-search">
            			<form action="#" method="post">
            				<div class="form-row">
            					<input type="text" onclick="this.value='';" onfocus="this.select()" onblur="this.value=!this.value?'Search':this.value;" value="Search" />
            				</div>
            			</form>
            		</div>
            		<div class="block-filter-option block-filter-option-status">
            			<select class="uniform">
            				<option>Status: All</option>
            				<option>Status: Open</option>
            				<option>Status: Closed</option>
            			</select>
            		</div>
            		<div class="block-filter-option block-filter-option-difficulty">
	            		<select class="uniform">
	            			<option>Difficulty: All</option>
	            			<option>Difficulty: Easy</option>
	            			<option>Difficulty: Medium</option>
	            			<option>Difficulty: Difficult</option>
	            		</select>
            		</div>
            	</div>
            	<div class="block-filter-sort">
            		Sort by: <a href="javascript:void(0)" class="block-filter-sort-link block-filter-sort-deadline">Deadline</a>
            	</div>
                <span class="task-group-title">Tasks pending my approval/publishing</span>
                <div class="task-single task-single-admin task-single-in-progress level-difficult clearfix">
                    <div class="cog"></div>
                    <div class="task-single-check"><input type="checkbox" class="task-single-checkbox" /></div>
                    <div class="task-single-content clearfix">
                        <div class="task-single-admin-btns clearfix">
                        	<form action="#" method="post">
                        	<input type="submit" class="task-btn task-btn-delete" value="Delete" />
                        	<input type="submit" class="task-btn task-btn-edit" value="Edit" />
                        	<input type="submit" class="task-btn task-btn-publish" value="Publish" />
                        	<input type="submit" class="task-btn task-btn-approve" value="Approve" />
                        	</form>
                        </div>
                        <span class="task-single-title"><a href="javascript:void(0)">Update Image Import Module</a></span>
                        <div class="task-single-content-bottom clearfix">
                            <div class="task-single-content-col1">
                                <span class="task-single-info task-single-student">Mentor: <a href="javascript:void(0)">Will Godwin</a></span>
                                <span class="task-single-info task-single-difficulty">Difficulty: <span class="emph">Difficult</span></span>
                            </div>
                            <div class="task-single-content-col2">
                                <span class="task-single-info task-single-deadline">Deadline: July 21 2011 12:13GMT</span>
                            </div>
                            <div class="task-single-content-col3">
                            </div>
                        </div>
                    </div>
                </div>
                <!-- end .task-single -->
                <div class="task-single task-single-admin task-single-in-progress level-easy even clearfix">
                    <div class="cog"></div>
                    <div class="task-single-check"><input type="checkbox" class="task-single-checkbox" /></div>
                    <div class="task-single-content clearfix">
                        <div class="task-single-admin-btns clearfix">
                        	<form action="#" method="post">
                            <input type="submit" class="task-btn task-btn-delete" value="Delete" />
                        	<input type="submit" class="task-btn task-btn-edit" value="Edit" />
                        	<input type="submit" class="task-btn task-btn-publish" value="Publish" />
                        	<input type="submit" class="task-btn task-btn-approve" value="Approve" />
                        	</form>
                        </div>
                        <span class="task-single-title"><a href="javascript:void(0)">Translate Documentation from English to Arabic</a></span>
                        <div class="task-single-content-bottom clearfix">
                            <div class="task-single-content-col1">
                                <span class="task-single-info task-single-student">Student: <a href="javascript:void(0)">Emma Goldman</a></span>
                                <span class="task-single-info task-single-difficulty">Difficulty: <span class="emph">Easy</span></span>
                            </div>
                            <div class="task-single-content-col2">
                                <span class="task-single-info task-single-deadline">Deadline: July 22 2011 2:21GMT</span>
                            </div>
                            <div class="task-single-content-col3">
                            </div>
                        </div>
                    </div>
                </div>
                <!-- end .task-single -->
                <div class="task-group-actions clearfix">
                    <div class="task-group-actions-select-all">
                        <span class="task-group-actions-select-all-text">All:</span> <input type="checkbox" name="chkall" class="task-group-actions-select-all-checkbox" />
                    </div>
                    <form action="#" method="post">
                    <input type="submit" class="task-btn task-btn-approve" value="Approve" />
                    <input type="submit" class="task-btn task-btn-publish" value="Publish" />
                    </form>
                </div>
                <!-- end .task-group-actions -->
                <div class="task-group-pager block-pager clearfix">
                    <ul class="menu-center-inline">
                        <li class="current">1</li>
                        <li><a href="javascript:void(0)">2</a></li>
                        <li><a href="javascript:void(0)">3</a></li>
                        <li><a href="javascript:void(0)">4</a></li>
                        <li><a href="javascript:void(0)">Next></a></li>
                        <li><a href="javascript:void(0)">Last></a></li>
                    </ul>
                </div>
                <!-- end .task-group-pager -->
            </div>
            <div id="all-tasks" class="task-group">
            	<div class="block-filter clearfix">
            		<div class="block-filter-option block-filter-option-search">
            			<form action="#" method="post">
            				<div class="form-row">
            					<input type="text" onclick="this.value='';" onfocus="this.select()" onblur="this.value=!this.value?'Search':this.value;" value="Search" />
            				</div>
            			</form>
            		</div>
            		<div class="block-filter-option block-filter-option-status">
            			<select class="uniform">
            				<option>Status: All</option>
            				<option>Status: Open</option>
            				<option>Status: Closed</option>
            			</select>
            		</div>
            		<div class="block-filter-option block-filter-option-difficulty">
            			<select class="uniform">
            				<option>Difficulty: All</option>
            				<option>Difficulty: Easy</option>
            				<option>Difficulty: Medium</option>
            				<option>Difficulty: Difficult</option>
            			</select>
            		</div>
            	</div>
            	<div class="block-filter-sort">
            		Sort by: <a href="javascript:void(0)" class="block-filter-sort-link block-filter-sort-deadline">Deadline</a>
            	</div>
                <span class="task-group-title">My Tasks</span>
                <div class="task-single level-easy task-single-in-progress clearfix">
                    <div class="cog"></div>
                    <div class="task-single-content clearfix">
                        <span class="task-single-title"><a href="javascript:void(0)">Translate Documentation from English to Arabic</a></span>
                        <form action="#" method="post">
                        <input type="submit" class="task-btn task-btn-delete" value="Delete" />
                        <input type="submit" class="task-btn task-btn-edit" value="Edit" />
                        </form>
                        <div class="task-single-content-bottom clearfix">
                            <div class="task-single-content-col1">
                                <span class="task-single-info task-single-student">Student: <a href="javascript:void(0)">Emma Goldman</a></span>
                                <span class="task-single-info task-single-difficulty">Difficulty: <span class="emph">Easy</span></span>
                            </div>
                            <div class="task-single-content-col2">
                                <span class="task-single-info task-single-deadline">Deadline: July 22 2011 2:21GMT</span>
                                <span class="task-single-info task-single-status">Status: <span class="emph">In progress</span></span>
                            </div>
                            <div class="task-single-content-col3">
                            </div>
                        </div>
                    </div>
                </div>
                <!-- end .task-single -->
                <div class="task-single level-difficult task-single-in-progress even clearfix">
                    <div class="cog"></div>
                    <div class="task-single-content clearfix">
                        <span class="task-single-title"><a href="javascript:void(0)">Update Image Import Module</a></span>
                        <form action="#" method="post">
                        <input type="submit" class="task-btn task-btn-delete" value="Delete" />
                        <input type="submit" class="task-btn task-btn-edit" value="Edit" />
                        </form>
                        <div class="task-single-content-bottom clearfix">
                            <div class="task-single-content-col1">
                                <span class="task-single-info task-single-student">Student: <a href="javascript:void(0)">Alex Berkman</a></span>
                                <span class="task-single-info task-single-difficulty">Difficulty: <span class="emph">Difficult</span></span>
                            </div>
                            <div class="task-single-content-col2">
                                <span class="task-single-info task-single-deadline">Deadline: July 21 2011 12:21GMT</span>
                                <span class="task-single-info task-single-status">Status: <span class="emph">In progress</span></span>
                            </div>
                            <div class="task-single-content-col3">
                            </div>
                        </div>
                    </div>
                </div>
                <!-- end .task-single -->
            </div>
        </div>
        <!-- end .block.block-user-tabs -->
    </div>
    <!-- end .grid_9.main -->

<?php include '../includes/footer.php'?>