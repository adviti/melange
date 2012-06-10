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
        <div class="block-filter-option block-filter-option-program-year">
          <label>Program Year:</label>
          <select class="uniform">
            <option>2011 (current)</option>
            <option>2010</option>
          </select>
        </div>
        <div class="block block-user-message">
            You have 1 task that needs review. Let's test <a href="javascript:void(0)">another link</a>. <a href="javascript:void(0)" class="more">Click here</a>
        </div>
        <!-- end .block.block-user-message -->
        <div class="block block-user-welcome clearfix">
            <div class="block-user-welcome-title">
                <span class="subhead">Mentor name</span>
                <span class="name">Maya Jones</span>
            </div>
            <form action="#" method="post">
            	<input type="submit" class="btn" value="Create a task" />
            </form>
        </div>
        <!-- end .block.block-user-welcome -->
        <div class="block block-tabs block-user-tabs">
            <ul>
            	<li><a href="#active-tasks">Active tasks</a></li>
            	<li><a href="#pending-tasks">Pending tasks</a></li>
            	<li><a href="#inactive-tasks">Inactive tasks</a></li>
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
                <span class="task-group-title">My Tasks</span>
                <div class="task-single task-single-in-progress level-difficult clearfix">
                    <div class="cog"></div>
                    <div class="task-single-content clearfix">
                        <span class="task-single-title"><a href="javascript:void(0)">Update Image Import Module</a></span>
                        <form action="#" method="post">
                        <input type="submit" class="task-btn task-btn-delete" value="Delete" />
                        <input type="submit" class="task-btn task-btn-edit" value="Edit Task" />
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
                <div class="task-single task-single-in-progress level-easy even clearfix">
                    <div class="cog"></div>
                    <div class="task-single-content clearfix">
                        <span class="task-single-title"><a href="javascript:void(0)">Translate Documentation from English to Arabic</a></span>
                        <form action="#" method="post">
                        <input type="submit" class="task-btn task-btn-delete" value="Delete" />
                        <input type="submit" class="task-btn task-btn-edit" value="Edit Task" />
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
                <div class="task-single task-single-in-progress level-medium clearfix">
                    <div class="cog"></div>
                    <div class="task-single-content clearfix">
                        <span class="task-single-title"><a href="javascript:void(0)">Translate Upload Documentation from English to Arabic</a></span>
                        <form action="#" method="post">
                        <input type="submit" class="task-btn task-btn-delete" value="Delete" />
                        <input type="submit" class="task-btn task-btn-edit" value="Edit Task" />
                        </form>
                        <div class="task-single-content-bottom clearfix">
                            <div class="task-single-content-col1">
                                <span class="task-single-info task-single-student">Student: <a href="javascript:void(0)">Mike Bakunin</a></span>
                                <span class="task-single-info task-single-difficulty">Difficulty: <span class="emph">Medium</span></span>
                            </div>
                            <div class="task-single-content-col2">
                                <span class="task-single-info task-single-deadline">Deadline: July 23 2011 2:21GMT</span>
                                <span class="task-single-info task-single-status">Status: <span class="emph">In progress</span></span>
                            </div>
                            <div class="task-single-content-col3">
                            </div>
                        </div>
                    </div>
                </div>
                <!-- end .task-single -->
            	<span class="task-group-title">All Tasks</span>
            	<div class="task-single task-single-in-progress level-difficult clearfix">
            	    <div class="cog"></div>
            	    <div class="task-single-content clearfix">
            	        <span class="task-single-title"><a href="javascript:void(0)">Update Image Import Module</a></span>
            	        <form action="#" method="post">
            	        <input type="submit" class="task-btn task-btn-delete" value="Delete" />
            	        <input type="submit" class="task-btn task-btn-edit" value="Edit Task" />
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
            	<div class="task-single level-easy task-single-in-progress even clearfix">
            	    <div class="cog"></div>
            	    <div class="task-single-content clearfix">
            	        <span class="task-single-title"><a href="javascript:void(0)">Translate Documentation from English to Arabic</a></span>
            	        <form action="#" method="post">
            	        <input type="submit" class="task-btn task-btn-delete" value="Delete" />
            	        <input type="submit" class="task-btn task-btn-edit" value="Edit Task" />
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
            	<div class="task-single level-medium task-single-complete clearfix">
            	    <div class="cog"></div>
            	    <div class="task-single-content clearfix">
            	        <span class="task-single-title"><a href="javascript:void(0)">Translate Upload Documentation from English to Arabic</a></span>
            	        <form action="#" method="post">
            	        <input type="submit" class="task-btn task-btn-delete" value="Delete" />
            	        <input type="submit" class="task-btn task-btn-edit" value="Edit Task" />
            	        </form>
            	        <div class="task-single-content-bottom clearfix">
            	            <div class="task-single-content-col1">
            	                <span class="task-single-info task-single-student">Student: <a href="javascript:void(0)">Mike Bakunin</a></span>
            	                <span class="task-single-info task-single-difficulty">Difficulty: <span class="emph">Medium</span></span>
            	            </div>
            	            <div class="task-single-content-col2">
            	                <span class="task-single-info task-single-deadline">Deadline: July 23 2011 2:21GMT</span>
            	                <span class="task-single-info task-single-status">Status: <span class="emph">Complete</span></span>
            	            </div>
            	            <div class="task-single-content-col3">
            	            </div>
            	        </div>
            	    </div>
            	</div>
            	<!-- end .task-single -->
            </div>
            <div id="pending-tasks" class="task-group">
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
                        <input type="submit" class="task-btn task-btn-edit" value="Edit Task" />
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
                        <input type="submit" class="task-btn task-btn-edit" value="Edit Task" />
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
            <div id="inactive-tasks" class="task-group">
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
            	<span class="task-group-title">All Tasks</span>
            	<div class="task-single level-difficult task-single-in-progress clearfix">
            	    <div class="cog"></div>
            	    <div class="task-single-content clearfix">
            	        <span class="task-single-title"><a href="javascript:void(0)">Update Image Import Module</a></span>
            	        <form action="#" method="post">
            	        <input type="submit" class="task-btn task-btn-delete" value="Delete" />
            	        <input type="submit" class="task-btn task-btn-edit" value="Edit Task" />
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
            </div>
        </div>
        <!-- end .block.block-user-tabs -->
    </div>
    <!-- end .grid_9.main -->

<?php include '../includes/footer.php'?>
