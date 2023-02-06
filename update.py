#!python3

from pathlib import Path
import coloredlogs
from git import Repo
from datetime import datetime
import os
import shutil
import logging
import colorama
import hashlib
import base64
from distutils.dir_util import copy_tree

def sha256sum(filename):
    h  = hashlib.sha256()
    b  = bytearray(128*1024)
    mv = memoryview(b)
    with open(filename, 'rb', buffering=0) as f:
        for n in iter(lambda : f.readinto(mv), 0):
            h.update(mv[:n])
    return h.hexdigest()

logger = logging.getLogger(__name__)

def log_header(msg):
	logger.info(colorama.Back.WHITE + colorama.Fore.BLACK + msg + colorama.Style.RESET_ALL)

def addLoggingLevel(levelName, levelNum, methodName=None):
	"""
	Comprehensively adds a new logging level to the `logging` module and the
	currently configured logging class.

	`levelName` becomes an attribute of the `logging` module with the value
	`levelNum`. `methodName` becomes a convenience method for both `logging`
	itself and the class returned by `logging.getLoggerClass()` (usually just
	`logging.Logger`). If `methodName` is not specified, `levelName.lower()` is
	used.

	To avoid accidental clobberings of existing attributes, this method will
	raise an `AttributeError` if the level name is already an attribute of the
	`logging` module or if the method name is already present 

	Example
	-------
	>>> addLoggingLevel('TRACE', logging.DEBUG - 5)
	>>> logging.getLogger(__name__).setLevel("TRACE")
	>>> logging.getLogger(__name__).trace('that worked')
	>>> logging.trace('so did this')
	>>> logging.TRACE
	5

	"""
	if not methodName:
		methodName = levelName.lower()

	if hasattr(logging, levelName):
		raise AttributeError('{} already defined in logging module'.format(levelName))
	if hasattr(logging, methodName):
		raise AttributeError('{} already defined in logging module'.format(methodName))
	if hasattr(logging.getLoggerClass(), methodName):
		raise AttributeError('{} already defined in logger class'.format(methodName))

	# This method was inspired by the answers to Stack Overflow post
	# http://stackoverflow.com/q/2183233/2988730, especially
	# http://stackoverflow.com/a/13638084/2988730
	def logForLevel(self, message, *args, **kwargs):
		if self.isEnabledFor(levelNum):
			self._log(levelNum, message, args, **kwargs)
	def logToRoot(message, *args, **kwargs):
		logging.log(levelNum, message, *args, **kwargs)

	logging.addLevelName(levelNum, levelName)
	setattr(logging, levelName, levelNum)
	setattr(logging.getLoggerClass(), methodName, logForLevel)
	setattr(logging, methodName, logToRoot)

def update_repos():
	log_header("01. updating repos...")

	repos = Path("./repos/")
	for repoPath in repos.iterdir():
		if repoPath.is_dir():
			repo = Repo(repoPath)

			origin = repo.remotes.origin
			logger.info(f"update_repos/[{repoPath.name}]: {str(origin.url)}")
			
			logger.debug(f"update_repos/[{repoPath.name}]/stash: {repo.git.stash()}")
			
			for branch in ['master', 'main']:
				try:
					checkOut = repo.git.checkout(branch)
					logger.debug(f"update_repos/[{repoPath.name}]/check_out/{branch}")
					logger.trace(f"update_repos/[{repoPath.name}]/check_out/{branch}: {checkOut}")
				except Exception as e:
					pass
			
			pulled = origin.pull()
			for remote in pulled:
				logger.debug(f"update_repos/[{repoPath.name}]/pull: {remote}")
			
			for submodule in repo.submodules:
				logger.debug(f"update_repos/[{repoPath.name}]/submodule: {submodule.update(init=True)}")

def build_pkg():
	LOG_PREFIX=f"build_pkg"
	log_header("02. building new package...")
	packageName=datetime.now().strftime("%Y-%m-%d") #_%H-%M")
	logger.info(f"{LOG_PREFIX}: {packageName}")
	packagePath=f"./builds/{packageName}/"

	pkgSpec = []

	if os.path.isdir(packagePath):
		logger.warning(f"{LOG_PREFIX}/path: {packageName} already exists, deleting")
		shutil.rmtree(Path(packagePath))

	package = Path(packagePath).mkdir(exist_ok=True)
	logger.trace(f"{LOG_PREFIX}/path: {packageName} created")

	repos = Path("./repos/")
	for repoPath in repos.iterdir():
		if repoPath.is_dir():
			LLP=f"{LOG_PREFIX}/repo([{repoPath.name[:10]}])"
			logger.info(f"{LLP}: {repoPath.name}")
			repoCfgFile=Path(f"{repoPath}.txt")
			if repoCfgFile.is_file():
				logger.trace(f"{LLP}/cfg: {repoCfgFile}")
				with repoCfgFile.open() as cfgFile:

					repo = Repo(repoPath)
					repoOriginEncoded = base64.b64encode(repo.remotes.origin.url.encode("ascii")).decode("ascii")
					repoCommit = repo.head.commit.hexsha
					cfgChecksum= sha256sum(repoCfgFile)
					repoSpec = f"{repoPath.name},{repoOriginEncoded},{repoCommit},{cfgChecksum}"
					pkgSpec.append(repoSpec)
					logger.trace(f"{LLP}/spec: {repoSpec}")

					for cfgFileLine in cfgFile.readlines():
						try:
							srcPath=cfgFileLine.split(",")[0].strip()
							dstPath=cfgFileLine.split(",")[1].strip()
							fileSpec=cfgFileLine.split(",")[2].strip()
							src=Path(f"{repoPath}/{srcPath}")
							dst=Path(f"{packagePath}/{dstPath}/")

							logger.trace(f"{LLP}/cfg/cmd/parse: VALID ([{srcPath}] @ [{fileSpec}] -> [{dstPath}])")

							if not (src.is_dir() or src.is_file()):
								raise Exception(f"source {src} does not exist")

							logger.trace(f"{LLP}/cfg/cmd/exec/src: {src}")

							ignore_func = lambda d, files: [f for f in files if f[0]=="." or (Path(f"{d}/{f}").is_file() and f[-len(fileSpec):] != fileSpec)]
							# TODO: improve me; but in general this ignores hidden files/dirs and *files* that don't match fileSpec

							result = shutil.copytree(src, dst, ignore=ignore_func)
							logger.trace(f"{LLP}/cfg/cmd/exec/dst: {result}")

						except IndexError as e:
							logger.warning(f"{LLP}/cfg/cmd/parse: INVALID ([{cfgFileLine.strip()}])")
							logger.trace(f"{LLP}/cfg/cmd/parse: INVALID ({e})")
							pass
						except Exception as e:
							logger.warning(f"{LLP}/cfg/cmd/exec: FAIL ([{cfgFileLine.strip()}])")
							logger.trace(f"{LLP}/cfg/cmd/exec: FAIL ({e})")
							pass

			else:
				logger.warning(f"{LLP}/cfg: {repoCfgFile} does not exists - skipping")
				pass
	
	buildSpecFilePath=Path(f"{packagePath}/spec.txt")
	with buildSpecFilePath.open("w") as buildSpecFile:
		for pkgSpecEntry in pkgSpec:
			buildSpecFile.writelines(f"{pkgSpecEntry}\n")

	buildReportFilePath=Path(f"{packagePath}/report.txt")
	with buildReportFilePath.open("w") as buildReportFile:
		for f in Path(packagePath).glob('**/*'):
			if Path(f).is_file():
				entry=str(f).replace(packagePath[2:],"")
				buildReportFile.writelines(f"{entry}\n")

	buildSpecDigest=sha256sum(buildSpecFilePath)
	logger.trace(f"{LOG_PREFIX}/digest: {buildSpecDigest}")

	return packagePath

def install_pkg(packagePath, flipperSDCardRoot):
	LOG_PREFIX=f"install_pkg"
	log_header("03. installing package...")

	sourceSpec=Path(f"{packagePath}/spec.txt")
	sourceDigest=sha256sum(sourceSpec)

	targetSpec=Path(f"{flipperSDCardRoot}/spec.txt")
	if targetSpec.is_file():
		logger.trace(f"{LOG_PREFIX}/targetSpec: {targetSpec} exists - checking")
		targetDigest=sha256sum(targetSpec)
		logger.trace(f"{LOG_PREFIX}/sourceDigest: {sourceDigest}")
		logger.trace(f"{LOG_PREFIX}/targetDigest: {targetDigest}")
		if sourceDigest == targetDigest:
			logger.info(f"{LOG_PREFIX}: target digest matches - no need to update")
			return True
		else:
			logger.info(f"{LOG_PREFIX}: target digest does not match, will update")

	targetReport=Path(f"{flipperSDCardRoot}/report.txt")
	if targetReport.is_file():
		logger.info(f"{LOG_PREFIX}/targetReport: {targetReport} exists - deleting previous package")
		with targetReport.open("r") as targetReportFile:
			for targetReportEntryLine in targetReportFile.readlines():
				targetReportEntry = targetReportEntryLine.strip()
				logger.trace(f"{LOG_PREFIX}/targetReport/delete: {targetReportEntry}")
				Path(f"{flipperSDCardRoot}/{targetReportEntry}").unlink(missing_ok=True)

	result = copy_tree(packagePath, flipperSDCardRoot)
	filesCopied=0
	for f in result:
		filesCopied+=1
		logger.trace(f"{LOG_PREFIX}/copytree/copy: {f}")
	logger.info(f"{LOG_PREFIX}/copytree/count: {filesCopied}")
	
if __name__ == "__main__":
	addLoggingLevel("TRACE", logging.DEBUG - 5)
	coloredlogs.install(fmt='%(asctime)s,%(msecs)03d %(name)s[%(process)d] %(levelname)s\t%(message)s')
	coloredlogs.set_level("INFO")
	#coloredlogs.set_level("DEBUG")
	#coloredlogs.set_level("TRACE")
	logging.getLogger("git").setLevel(logging.ERROR)

	update_repos()
	packagePath = build_pkg()
	install_pkg(packagePath, "/Volumes/FlipperSD")
	log_header("04. installed successfully")
